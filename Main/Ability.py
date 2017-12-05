from direct.task.Task import Task


class Ability(object):
    def __init__(self, inp, cooldown, ability, base):
        self.usable = True
        self.cooldown = cooldown
        self.base = base
        self.ability = ability
        self.base.accept(inp, self.use)

    def use(self):
        if self.usable:
            self.ability()
            self.usable = False
            self.base.taskMgr.doMethodLater(self.cooldown, self.reset, "cooldown")

    def reset(self, task):
        self.usable = True
        return Task.done
