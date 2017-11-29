from direct.actor.Actor import Actor, CollisionNode, CollisionSphere, \
    CollisionHandlerPusher
from direct.task import Task
from Projectile import Projectile

class Character:
    def __init__(self, model, scale, pos, render, animations, base, path, health):
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
        self.fromObj = self.actor.attachNewNode(CollisionNode('cnode'))
        self.fromObj.node().addSolid(CollisionSphere(*coords))
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.fromObj, self.actor)
        self.fromObj.show()
        self.life = health
        self.currLife = health

    def fire(self):
        self.bullet = Projectile(self.base, self.path, "/bullet.egg",
                                 self.actor, 10, self.render)
        self.bullet.fire()

    def moveY(self, y):
        self.y = y

    def moveZ(self, z):
        self.z = z

    def getX(self):
        return self.actor.getX()

    def getY(self):
        return self.actor.getY()

    def getLife(self):
        return self.currLife

    def maxLife(self):
        return self.life

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