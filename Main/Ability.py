from direct.task.Task import Task

from Character import *


class Ability(object):
    def __init__(self, inp, cooldown, ability, base, character):
        self.usable = True
        self.cooldown = cooldown
        self.base = base
        self.ability = ability
        self.character = character
        self.inp = inp

    def use(self):
        if self.usable:
            self.abili()
            self.usable = False
            self.base.taskMgr.doMethodLater(self.cooldown, self.reset, "cooldown")

    def abili(self):
        eval("self.character." + self.ability)

    def reset(self, task):
        self.usable = True
        return Task.done
