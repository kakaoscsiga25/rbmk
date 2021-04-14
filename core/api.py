import core.reactor_factory as factory

def get_tick_time(reactor = factory.get_reactor()):
    return reactor.tick_time

def do_tick(reactor = factory.get_reactor()):
    reactor.do_tick()

def K2C(K):
    return K - 273.
def Pa2Bar(p):
    return p / 1e5

########################################################################

def set_controlling_rod(percent, reactor = factory.get_reactor()): # [0,100]
    reactor.core.controlling_rods = percent / 100.

def set_reactor_pump_performance(percent, reactor = factory.get_reactor()): # [0,100]
    reactor.core.pump_performance = percent / 100.

def set_steam_circuit_pump_performance(percent, reactor = factory.get_reactor()): # [0,100]
    reactor.steam_circuit.pump_performance = percent / 100.

#########################################################################

def get_temperature_water_before_reactor(reactor = factory.get_reactor()):
    return K2C(reactor.core.water_pipe_before_reactor.getTemperature(reactor.core.pressure))

def get_temperature_water_reactor(reactor = factory.get_reactor()):
    return K2C(reactor.core.water_reactor.getTemperature(reactor.core.pressure))

def get_temperature_water_after_reactor(reactor = factory.get_reactor()):
    return K2C(reactor.core.water_pipe_after_reactor.getTemperature(reactor.core.pressure))

def get_temperature_water_in_separator_core_circuit(reactor = factory.get_reactor()):
    return K2C(reactor.core.water_separator.getTemperature(reactor.core.pressure))

def get_steam_in_reactor(reactor = factory.get_reactor()):
    return reactor.core.steam_in_reactor_core * 100. # to percent

def get_pressure(reactor = factory.get_reactor()):
    return Pa2Bar(reactor.core.pressure)



def get_temperature_water_in_separator_steam_circuit(reactor = factory.get_reactor()):
    return K2C(reactor.steam_circuit.water_separator.getTemperature(reactor.steam_circuit.pressure))

def get_temperature_water_after_separator(reactor = factory.get_reactor()):
    return K2C(reactor.steam_circuit.water_pipe_after_separator.getTemperature(reactor.steam_circuit.pressure))

def get_temperature_water_after_turbines(reactor = factory.get_reactor()):
    return K2C(reactor.steam_circuit.water_pipe_after_turbines.getTemperature(reactor.steam_circuit.pressure))

def get_temperature_water_before_separator(reactor = factory.get_reactor()):
    return K2C(reactor.steam_circuit.water_pipe_before_separator.getTemperature(reactor.steam_circuit.pressure))

def get_output_power(reactor = factory.get_reactor()):
    return reactor.steam_circuit.power_output

