import numpy as np
from core.reactor_core import Reactor_core
from core.reactor_steam_circuit import Reactor_steam_circuit

class Reactor:
    tick_time = 5

    # Init vals
    init_temperature = 273 + 24  # Kelvin


    def __init__(self):
        self.core = Reactor_core()
        self.steam_circuit = Reactor_steam_circuit()

    def do_tick(self):
        self.core.chain_reaction(steam_circuit=self.steam_circuit, tick_time=self.tick_time)



