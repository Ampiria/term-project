from random import randint

from direct.actor.Actor import Actor, CollisionNode, CollisionSphere, CollisionHandlerQueue
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from direct.task import Task

from Ability import Ability
from Projectile import Projectile
import math

class Character(object):
    def __init__(self, model, scale, pos, render, animations, base, path, health, name):
        self.startPos = pos
        self.actor = Actor(model, animations)
        self.actor.setScale(scale)
        self.actor.setPos(pos)
        self.actor.reparentTo(render)
        self.render = render
        self.base = base
        self.y, self.z, self.up = 0, 0, 0
        self.path = path
        self.life = health
        self.currLife = health
        self.fired = False
        self.fireOnCooldown = False
        self.fireCooldown = 2
        self.fireCooldownStart = 42
        bounds = self.actor.getChild(0).getBounds()
        c = bounds.getCenter()
        r = bounds.getRadius() * 1.005
        self.colS = CollisionSphere(c, r)
        self.colN = CollisionNode(name)
        self.colN.addSolid(self.colS)
        self.pColN = self.actor.attachNewNode(self.colN)
        self.colHand = CollisionHandlerQueue()
        self.base.cTrav.addCollider(self.pColN, self.colHand)
        self.base.taskMgr.add(self.move, "Move")
        self.base.taskMgr.add(self.update, "upd")
        self.projList = []
        self.roundSyms = dict()
        self.rounds = 0
        self.lost = False
        self.win = False
        self.abilities = []
        self.healUp = Ability("j", 4, "heal()", self.base, self)
        self.ultAbil = Ability("k", 15, "ult()", self.base, self)
        self.abilities.append(self.ultAbil)
        self.abilities.append(self.healUp)

    def fire(self):
        self.bullet = Projectile(self.base, self.path, "/bullet.egg",
                                 self.actor, 10, self.render, self)
        self.bullet.fire()

    def moveY(self, y):
        self.y = y

    def moveZ(self, z):
        self.z = z

    def getX(self):
        return self.actor.getX()

    def getY(self):
        return self.actor.getY()

    def getPos(self):
        return self.actor.getPos()

    def getHpr(self):
        return self.actor.getHpr()

    def getLife(self):
        return self.currLife

    def maxLife(self):
        return self.life

    def reset(self):
        self.actor.setPos(self.startPos)
        self.currLife = self.life
        self.lost = False

    def collisions(self):
        for coll in self.colHand.getEntries():
            if coll.getInto() == self.colS:
                self.changeLife(-10)

    def changeLife(self, amount):
        self.currLife += amount
        if self.currLife > self.life:
            self.currLife = self.life
        if self.currLife <= 0:
            self.lost = True
            self.base.roundOv = True

    def move(self, task):
        if self.y == 0:
            self.actor.loop("walk")
        self.actor.setPos(self.actor, 0, self.y, self.up)
        if self.actor.getPos()[0] > 990 or self.actor.getPos()[0] < 30:
            self.actor.setPos(self.actor, 0, -self.y, 0)
        if self.actor.getPos()[1] > 990 or self.actor.getPos()[1] < 30:
            self.actor.setPos(self.actor, 0, -self.y, 0)
        self.actor.setHpr(self.actor, self.z, 0, 0)
        return Task.cont

    def heal(self):
        self.changeLife(20)

    def ult(self):
        ult = Projectile(self.base, self.path, "/bullet.egg",
                                 self.actor, 30, self.render, self)
        ult.fire()

    def wonRound(self):
        pos = (-0.6 + self.rounds * 0.1, 0, self.base.a2dBottom + 0.25) if not \
            isinstance(self, AI) else (0.5 + self.rounds * 0.1, 0, self.base.a2dTop - 0.3)
        self.roundSyms["rounds%d" % self.rounds] = OnscreenImage(
            image=self.path + "/round.png",
            pos=pos,
            scale=0.1)
        self.roundSyms["rounds%d" % self.rounds].setTransparency(
            TransparencyAttrib.MAlpha)
        self.roundSyms["rounds%d" % self.rounds].reparentTo(self.base.render2d)

    def update(self, task):
        if self.rounds >= 3:
            self.win = True
            self.base.gameOver = True
        if self.base.roundOv:
            self.base.roundOv = False
            if not self.lost:
                self.rounds += 1
                self.wonRound()
            self.base.player.reset()
            try:
                self.base.ai.reset()
            except:
                pass
        if self.fireOnCooldown:
            if self.base.clock.get_long_time() - self.fireCooldownStart <= self.fireCooldown:
                self.fireOnCooldown = False
        return Task.cont


class AI(Character):
    def __init__(self, model, scale, pos, render, animations, base, path, health,
                 rate=8):
        super(AI, self).__init__(model, scale, pos, render, animations, base, path,
                                 health, "ai")
        self.base.taskMgr.add(self.ai, "ai")
        self.fireRate = rate

    def ai(self, ai):
        if not self.base.gameOver:
            self.chaseTarget()
            self.heel()
        else:
            self.moveZ(0)
            self.moveY(0)
        return Task.cont

    def heel(self):
        if self.currLife <= self.life - 20:
            self.healUp.use()

    def chaseTarget(self):
        a = math.degrees(math.atan2(self.base.player.getY() - self.actor.getY(),
                       self.base.player.getX() - self.actor.getX()))
        c = self.actor.getH()
        c -= 90
        c += 0 if c > 0 else 360
        a += 0 if a > 0 else 360

        if math.fabs(c - a) >= 5:
            if c - a < 0:
                self.moveZ(5)
            else:
                self.moveZ(-5)
        else:
            self.moveZ(0)
            if randint(1, 100) < self.fireRate and self.base.player.actor.getDistance(
                    self.actor) < 2000:
                self.fire()

        if self.base.player.actor.getDistance(self.actor) > 2000:
            self.moveY(-80)
        else:
            self.moveY(0)


class AdvancedAI(AI):
    def __init__(self, model, scale, pos, render, animations, base, path, health):
        super(AdvancedAI, self).__init__(model, scale, pos, render, animations, base,
                                         path, health, 14)

    def ai(self, ai):
        super(AdvancedAI, self).ai(ai)
        if not self.base.gameOver:
            self.avoid()
        return Task.cont

    def heel(self):
        if self.currLife < self.base.player.currLife:
            super(AdvancedAI, self).heel()

    def avoid(self):
        if self.currLife < 0.4 * self.life:
            a = math.degrees(math.atan2(self.base.player.getY() - self.actor.getY(),
                                        self.base.player.getX() - self.actor.getX()))
            c = self.actor.getH()
            c -= 90
            c += 0 if c > 0 else 360
            a += 0 if a > 0 else 360

            b = randint(int(a + 25), int(a + 360 - 25))
            print(b)

            if math.fabs(b - a) >= 5:
                if c - a < 0:
                    self.moveZ(5)
                else:
                    self.moveZ(-5)
            else:
                self.moveZ(0)

            if self.base.player.actor.getDistance(self.actor) <= 7000:
                self.moveY(-80)
            else:
                self.moveY(0)
