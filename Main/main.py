from direct.gui.DirectWaitBar import DirectWaitBar, ClockObject, CollisionHandlerEvent
from direct.showbase.ShowBase import *
from panda3d.core import Filename, GeoMipTerrain, CollisionTraverser
from Character import *
import os
import sys
import socket
import threading
from Queue import Queue

HOST = "128.237.197.120"
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST, PORT))
print("connected to server")


def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")


serverMsg = Queue(100)
threading.Thread(target=handleServerMsg, args=(server, serverMsg)).start()


class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.ai = None
        self.cTrav = CollisionTraverser()
        self.coll = CollisionHandlerEvent()
        self.coll.addInPattern("%fn-into-%in")
        self.clock = ClockObject()
        self.path = os.path.abspath(sys.path[0])
        self.path = Filename.fromOsSpecific(self.path).getFullpath()
        terrain = GeoMipTerrain("worldTerrain")
        terrain.setHeightfield("heightMap.png")
        terrain.setColorMap("colormap.png")
        terrain.setBruteforce(True)
        root = terrain.getRoot()
        root.reparentTo(self.render)
        root.setSz(1)
        terrain.generate()
        self.player = Character("models/panda-model", 0.05, (300, 300, 0),
                                self.render, {"walk": "models/panda-walk4"},
                                self, self.path, 200, "player")
        self.addControls()
        self.loadUI()
        self.startTasks()
        self.accept("proj-into-player", self.player.changeLife, [-1])
        self.others = dict()
        self.roundOv = False
        self.gameOver = False

    def startTasks(self):
        self.taskMgr.add(self.camra, "Cam")
        self.taskMgr.add(self.update, "Update")
        self.taskMgr.add(self.manageCollisions, "colls")

    def loadUI(self):
        self.lifeBar = DirectWaitBar(text="", value=self.player.life,
                                     barColor=(0, 1, 0.25, 1),
                                     barBorderWidth=(0.03, 0.03),
                                     borderWidth=(0.01, 0.01),
                                     frameColor=(0.5, 0.55, 0.70, 1),
                                     range=self.player.life,
                                     frameSize=(-1.2, 0, 0, -0.1),
                                     pos=(0.6, self.a2dLeft, self.a2dBottom + 0.15))
        self.lifeBar.setTransparency(1)
        self.lifeBar.reparentTo(self.render2d)
    def addControls(self):
        self.accept("w", self.moveY, [-80])
        self.accept("w-up", self.moveY, [0])
        self.accept("s", self.moveY, [80])
        self.accept("s-up", self.moveY, [0])
        self.accept("a", self.moveZ, [5])
        self.accept("a-up", self.moveZ, [0])
        self.accept("d", self.moveZ, [-5])
        self.accept("d-up", self.moveZ, [0])
        self.accept("space", self.fire)
        self.acceptOnce("o", self.aiBattle)

    def manageCollisions(self, task):
        self.cTrav.traverse(self.render)
        self.player.collisions()
        for a in self.others:
            self.others[a].collisions()
        return Task.cont

    def camra(self, task):
        self.camera.setPos(self.player.getX(), self.player.getY(), 750)
        self.camera.setHpr(10, 270, 100)
        return Task.cont

    def aiBattle(self):
        self.ai = AI("models/panda-model", 0.05, (700, 700, 0),
                                self.render, {"walk": "models/panda-walk4"},
                                self, self.path, 200)
        self.others["ai"] = self.ai
        self.aiLifebar = DirectWaitBar(text="", value=self.ai.life,
                                       barColor=(0, 1, 0.25, 1),
                                       barBorderWidth=(0.003, 0.003),
                                       borderWidth=(0.001, 0.001),
                                       frameColor=(0.5, 0.55, 0.70, 1),
                                       range=self.ai.life,
                                       frameSize=(-0.45, 0, 0, -0.1),
                                       pos=(1, 0, self.a2dTop - 0.11)
                                       )
        self.aiLifebar.setTransparency(1)
        self.aiLifebar.reparentTo(self.render2d)


    def moveY(self, amount):
        self.player.moveY(amount)
        msg = "moved y " + str(amount) + "\n"
        print("sending: ", msg)
        server.send(msg.encode())

    def moveZ(self, amount):
        self.player.moveZ(amount)
        msg = "moved z " + str(amount) + "\n"
        print("sending: ", msg)
        server.send(msg.encode())

    def fire(self):
        self.player.fire()
        msg = "fired\n"
        print ("sending: ", msg)
        server.send(msg.encode())

    def update(self, task):
        self.lifeBar['value'] = self.player.currLife
        self.lifeBar.setValue()
        if self.ai is not None:
            self.aiLifebar['value'] = self.ai.currLife
            self.aiLifebar.setValue()
        while serverMsg.qsize() > 0:
            msg = serverMsg.get(False)
            try:
                print("received: ", msg, "\n")
                msg = msg.split()
                command = msg[0]
                if command == "myIDis":
                    self.myPID = msg[1]

                elif command == "newPlayer":
                    n = msg[1]
                    self.others[n] = Character("models/panda-model", 0.05, (300, 300, 0),
                                               self.render,
                                               {"walk": "models/panda-walk4"}, self,
                                               self.path, 200, "play2")
                    self.taskMgr.add(self.others[n].move, "Move" + n)
                elif command == "moved":
                    PID = msg[1]
                    if msg[2] == "y":
                        self.others[PID].moveY(int(msg[3]))
                    else:
                        self.others[PID].moveZ(int(msg[3]))
                elif command == "fired":
                    PID = msg[1]
                    self.others[PID].fire()
            except:
                print("rip")
            serverMsg.task_done()
        return Task.cont


a = App()

a.run()
