from random import randint

from direct.actor.Actor import Actor, CollisionNode, CollisionSphere, \
    CollisionHandlerPusher, BitMask32, CollisionHandler, CollisionHandlerQueue, \
    CollisionTube
from direct.task import Task
from Projectile import Projectile
import math

class Character(object):
    def __init__(self, model, scale, pos, render, animations, base, path, health, name):
        self.actor = Actor(model, animations)
        self.actor.setScale(scale)
        self.actor.setPos(pos)
        self.actor.reparentTo(render)
        self.render = render
        self.base = base
        self.y, self.z = 0, 0
        self.path = path
        coords = list(self.actor.getPos()) + [2]
        coords = tuple(coords)
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
        self.pColN.show()
        self.colHand = CollisionHandlerQueue()
        self.base.accept("i", self.printBounds, [bounds])
        self.base.cTrav.addCollider(self.pColN, self.colHand)
        self.base.taskMgr.add(self.move, "Move")
        self.base.taskMgr.add(self.update, "upd")
        self.projList = []

    def printBounds(self, bounds):
        print(bounds)

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

    def collisions(self):
        for coll in self.colHand.getEntries():
            if coll.getInto() == self.colS:
                self.changeLife(-10)

    def changeLife(self, amount):
        self.currLife += amount
        if self.currLife > self.life:
            self.currLife = self.life
        if self.currLife < 0:
            self.currLife = 0

    def move(self, task):
        if self.y == 0:
            self.actor.loop("walk")
        self.actor.setPos(self.actor, 0, self.y, 0)
        if self.actor.getPos()[0] > 990 or self.actor.getPos()[0] < 30:
            self.actor.setPos(self.actor, 0, -self.y, 0)
        if self.actor.getPos()[1] > 990 or self.actor.getPos()[1] < 30:
            self.actor.setPos(self.actor, 0, -self.y, 0)
        self.actor.setHpr(self.actor, self.z, 0, 0)
        return Task.cont

    def update(self, task):
        if self.fireOnCooldown:
            if self.base.clock.get_long_time() - self.fireCooldownStart <= self.fireCooldown:
                self.fireOnCooldown = False
        return Task.cont

class AI(Character):
    def __init__(self, model, scale, pos, render, animations, base, path, health):
        super(AI, self).__init__(model, scale, pos, render, animations, base, path,
                                 health, "ai")
        self.base.taskMgr.add(self.ai, "ai")

    def ai(self, ai):
        self.chaseTarget()
        return Task.cont

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
            if randint(1, 100) < 5:
                self.fire()

        if self.base.player.actor.getDistance(self.actor) > 2000:
            pass  # self.moveY(-80)
        else:
            pass  # self.moveY(0)

