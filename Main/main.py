from direct.gui.DirectWaitBar import DirectWaitBar, TextNode
from direct.showbase.ShowBase import *
from panda3d.core import Filename, GeoMipTerrain, CollisionTraverser
from Character import *
import os
import sys
import socket
import threading
from Queue import Queue

HOST = "128.237.142.67"
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
                                self, self.path, 200)
        self.lifeBar = DirectWaitBar(text="Health", text_fg=(1, 1, 1, 1),
                                     text_pos=(-1.2, -0.18, 0),
                                     text_align=TextNode.ALeft,
                                     value=400, barColor=(0, 1, 0.25, 1),
                                     barBorderWidth=(0.03, 0.03), borderWidth=(0.01, 0.01),
                                     frameColor=(0.8, 0.05, 0.10, 1),
                                     frameSize=(-1.2, 0, 0, -0.1),
                                     pos=(-0.2, 0, self.a2dTop - 0.15))
        self.lifeBar.setTransparency(1)
        self.lifeBar.reparentTo(self.render2d)
        self.accept("w", self.moveY, [-80])
        self.accept("w-up", self.moveY, [0])
        self.accept("s", self.moveY, [80])
        self.accept("s-up", self.moveY, [0])
        self.accept("a", self.moveZ, [5])
        self.accept("a-up", self.moveZ, [0])
        self.accept("d", self.moveZ, [-5])
        self.accept("d-up", self.moveZ, [0])
        self.accept("space", self.fire)
        self.taskMgr.add(self.camra, "Cam")
        self.taskMgr.add(self.player.move, "Move")
        self.taskMgr.add(self.update, "Update")
        self.cTrav = CollisionTraverser('t')
        self.cTrav.traverse(self.render)
        self.others = dict()

    def camra(self, task):
        self.camera.setPos(self.player.getX(), self.player.getY(), 750)
        self.camera.setHpr(10, 270, 100)
        return Task.cont

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
                                               self.path, 200)
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
