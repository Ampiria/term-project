from math import *

from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from direct.interval.ProjectileInterval import ProjectileInterval, \
    CollisionSphere, CollisionNode
from direct.task.Task import Task

import Character



class Projectile(object):
    def __init__(self, base, path, p, actor, scale, render, character):
        self.proj = base.loader.loadModel(path + p)
        self.proj.setPos(actor.getPos())
        self.proj.setScale(scale)
        self.proj.setColor(255, 0, 120, 0.7)
        self.proj.reparentTo(render)
        self.base = base
        self.p = path + p
        self.actor = actor
        self.character = character
        bounds = self.proj.getChild(0).getBounds()
        c = bounds.getCenter()
        r = bounds.getRadius() * 1.01
        self.colSphere = CollisionSphere(c, r)
        self.colNode = CollisionNode('proj')
        self.colNode.addSolid(self.colSphere)
        self.projColNode = self.proj.attachNewNode(self.colNode)
        self.projColNode.show()
        if isinstance(self.character, Character.AI):
            try:
                self.base.cTrav.addCollider(self.projColNode, self.base.player.colHand)
                self.base.player.projList.append(self)
            except:
                pass
        else:
            try:
                self.base.cTrav.addCollider(self.projColNode, self.base.ai.colHand)
                self.base.ai.projList.append(self)
            except:
                pass

    def kill(self):
        self.proj.detachNode()
        self.character.fired = False

    def fire(self):
        endx = self.actor.getX() + 200 * cos(radians(self.actor.getH() - 90))
        endy = self.actor.getY() + 200 * sin(radians(self.actor.getH() - 90))
        self.interval = ProjectileInterval(self.proj,
                                           startPos=self.proj.getPos(),
                                           endPos=(endx, endy,
                                                   self.actor.getZ()),
                                           duration=0.1)
        self.sequence = None

        def start():
            if self.character.fired or self.character.fireOnCooldown:
                self.sequence = Sequence(Func(self.kill))
            else:
                self.character.fired = True
                self.character.fireOnCooldown = True
                self.character.fireCooldown = 3
                self.character.fireCooldown = self.base.clock.get_long_time()
                self.sequence = Sequence(self.interval, Func(self.kill))

        start()
        self.sequence.start()