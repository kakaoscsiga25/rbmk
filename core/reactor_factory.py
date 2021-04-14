import core.reactor

#todo: if needed

reactor = core.reactor.Reactor()

def get_reactor(id=""):
    return reactor

def get_default():
    return get_reactor("")
