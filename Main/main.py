from direct.gui.DirectButton import DirectButton
from direct.gui.DirectWaitBar import DirectWaitBar, ClockObject, CollisionHandlerEvent, \
    WindowProperties, DirectFrame
from direct.showbase.ShowBase import *
from panda3d.core import Filename, GeoMipTerrain, CollisionTraverser
from Character import *
import os
import sys
import socket
import threading
from Queue import Queue

HOST = "128.237.84.118"
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST, PORT))
print("connected to server")


def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
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
        self.prop = WindowProperties()
        self.prop.setSize(1920, 1080)
        self.prop.setMinimized(False)
        self.win.requestProperties(self.prop)
        self.path = os.path.abspath(sys.path[0])
        self.path = Filename.fromOsSpecific(self.path).getFullpath()
        self.fram = DirectFrame(frameColor=(0, 0, 0, 1),
                                frameSize=(-1, 1, -1, 1),
                                pos=(0, 0, 0),
                                image=self.path + "/start.png")
        self.fram.reparentTo(self.render2d)
        self.easyAI = DirectButton(text="Easy AI",
                                   command=self.easyPlay,
                                   pos=(0, 0, 0),
                                   scale=0.1,
                                   text_bg=(0, 0, 0, 1),
                                   text_fg=(255, 255, 255, 1))
        self.hardAI = DirectButton(text="Hard AI",
                                   command=self.hardPlay,
                                   pos=(0, 0, -0.2),
                                   scale=0.1,
                                   text_bg=(0, 0, 0, 1),
                                   text_fg=(255, 255, 255, 1))
        self.help = DirectButton(text="Help",
                                 command=self.helpScreen,
                                 pos=(0, 0, -0.4),
                                 scale=0.1,
                                 text_bg=(0, 0, 0, 1),
                                 text_fg=(255, 255, 255, 1))

    def easyPlay(self):
        self.play(True)

    def hardPlay(self):
        self.play(True, True)

    def helpScreen(self):
        self.easyAI.hide()
        self.hardAI.hide()
        self.help.hide()
        self.fram["image"] = self.path + "/help.jpg"
        self.fram.updateFrameStyle()
        self.back = DirectButton(text="",
                                 command=self.helpScreen,
                                 pos=(0, 0, -0.4),
                                 scale=0.1,
                                 text_bg=(0, 0, 0, 1),
                                 text_fg=(255, 255, 255, 1))


    def back(self):
        self.hardAI.show()
        self.easyAI.show()
        self.help.show()
        self.back.destroy()
        self.fram["image"] = self.path + "/start.png"

    def play(self, ai, difficult=False):
        self.easyAI.destroy()
        self.hardAI.destroy()
        self.ai = None
        self.cTrav = CollisionTraverser()
        self.coll = CollisionHandlerEvent()
        self.coll.addInPattern("%fn-into-%in")
        self.clock = ClockObject()
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
        self.taskMgr.add(self.update, "Update")
        self.gameOver = False
        if ai:
            self.aiBattle(difficult)

    def startTasks(self):
        self.taskMgr.add(self.camra, "Cam")
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
        for abil in self.player.abilities:
            self.accept(abil.inp, abil.use)

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

    def aiBattle(self, advanced=False):
        if not advanced:
            self.ai = AI("models/panda-model", 0.05, (700, 700, 0), self.render,
                         {"walk": "models/panda-walk4"}, self, self.path, 200)
        else:
            self.ai = AdvancedAI("models/panda-model", 0.05, (700, 700, 0),
                                 self.render, {"walk": "models/panda-walk4"}, self,
                                 self.path, 200)
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
