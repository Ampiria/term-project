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
                                self, self.path)
        self.accept("w", self.player.moveY, [-100])
        self.accept("w-up", self.player.moveY, [0])
        self.accept("s", self.player.moveY, [100])
        self.accept("s-up", self.player.moveY, [0])
        self.accept("a", self.player.moveZ, [5])
        self.accept("a-up", self.player.moveZ, [0])
        self.accept("d", self.player.moveZ, [-5])
        self.accept("d-up", self.player.moveZ, [0])
        self.accept("space", self.player.fire)
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

    def update(self, task):
        while serverMsg.qsize() > 0
            msg = serverMsg.get(False)
            try:
                print("received: ", msg, "\n")
                msg = msg.split()
                command = msg[0]

                if command ==

            except:
                print("rip")
            serverMsg.task_done()

a = App()

a.run()
