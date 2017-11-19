from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import *

class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        terrain = GeoMipTerrain("worldTerrain")
        terrain.setHeightfield("heightMap.png")
        terrain.setColorMap("colormap.png")
        terrain.setBruteforce(True)
        root = terrain.getRoot()
        root.reparentTo(self.render)
        root.setSz(1)
        terrain.generate()
        self.pandaActor = Actor("models/panda-model", {"walk":
                                                       "models/panda-walk4"})
        self.pandaActor.setScale(0.05, 0.05, 0.05)
        self.pandaActor.setPos(100, 100, 0)
        self.pandaActor.zDir = 0
        self.pandaActor.yDir = 0
        self.pandaActor.reparentTo(self.render)
        self.accept("w", self.moveY, [-100])
        self.accept("w-up", self.moveY, [0])
        self.accept("s", self.moveY, [100])
        self.accept("s-up", self.moveY, [0])
        self.accept("a", self.turnZ, [5])
        self.accept("a-up", self.turnZ, [0])
        self.accept("d", self.turnZ, [-5])
        self.accept("d-up", self.turnZ, [0])
        self.taskMgr.add(self.camra, "Cam")
        self.taskMgr.add(self.move, "Move")

    def moveY(self, amount):
        self.pandaActor.yDir = amount

    def turnZ(self, amount):
        self.pandaActor.zDir = amount

    def move(self, task):
        if self.pandaActor.yDir == 0:
            self.pandaActor.loop("walk")
        self.pandaActor.setPos(self.pandaActor, 0, self.pandaActor.yDir, 0)
        self.pandaActor.setHpr(self.pandaActor, self.pandaActor.zDir, 0, 0)
        return Task.cont

    def camra(self, task):
        self.camera.setPos(self.pandaActor.getX(), self.pandaActor.getY(), 750)
        self.camera.setHpr(10, 270, 100)
        return Task.cont

a = App()

a.run()
