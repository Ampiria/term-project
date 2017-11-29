from math import *

from direct.interval.FunctionInterval import Wait, Func
from direct.interval.MetaInterval import Sequence
from direct.interval.ProjectileInterval import ProjectileInterval, \
    CollisionSphere, CollisionNode, CollisionHandlerPusher


class Projectile:
    def __init__(self, base, path, p, actor, scale, render):
        self.proj = base.loader.loadModel(path + p)
        self.proj.setPos(actor.getPos())
        self.proj.setScale(scale)
        self.proj.setColor(255, 0, 120, 0.7)
        self.proj.reparentTo(render)
        coords = (actor.getX(),actor.getY(), actor.getZ(), scale)
        self.fromObj = self.proj.attachNewNode(CollisionNode('colNode'))
        self.fromObj.node().addSolid(CollisionSphere(*coords))
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.fromObj, self.proj)
        base.cTrav.addCollider(self.fromObj, self.pusher)
        self.fromObj.show()
        self.base = base
        self.p = path + p
        self.actor = actor

    def fire(self):
        endx = self.actor.getX() + 200 * cos(radians(self.actor.getH() - 90))
        endy = self.actor.getY() + 200 * sin(radians(self.actor.getH() - 90))
        self.interval = ProjectileInterval(self.proj,
                                           startPos=self.proj.getPos(),
                                           endPos=(endx, endy,
                                                   self.actor.getZ()),
                                           duration=0.1)
        def kill():
            self.proj.detachNode()
        self.sequence = Sequence(self.interval, Func(kill))

        self.sequence.start()
