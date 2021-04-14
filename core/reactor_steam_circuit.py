import copy
from core.water import Water

class Reactor_steam_circuit:
    def __init__(self):
        self.init_pressure = 1e5  # Pascal (N/m2)
        self.init_temperature = 273 + 24
        self.temperature_pressure_coeff = 2.6e4  # Pascal/K  todo more precise solution
        self.water_heat_capacity = 4.2  # MJ/(1000kg*K)      todo graph
        self.steam_heat_capacity = 2.  # MJ/(1000kg*K)       todo graph

        # Changeable
        self.pump_performance = 1. # percent

        # Observable
        self.water_separator = Water(2)
        self.water_pipe_before_separator = Water(1)
        self.water_pipe_after_separator = Water(1)
        self.water_pipe_after_turbines = Water(1)
        self.water_cooler = Water(2)

        # self.temperature_water_in_separator = 273 + 24
        # self.temperature_water_after_separator = 273 + 24
        # self.temperature_water_after_turbines = 273 + 24
        # self.temperature_water_before_separator = 273 + 24
        # self.water_in_separator = 2 # m3
        # self.water_in_pipe_after_separator = 1 # m3
        # self.water_in_pipe_before_separator = 1 # m3
        #self.steam_pressure_hp_turbine = self.init_pressure
        #self.turbine_rpm = 0.
        self.waterflow_max = 1 # m3/s
        self.power_output = 0. # MW
        self.pressure = 1e5

        # Constants
        #self.turbine_mass = 1 # TODO
        self.turbine_ece = 0.8 # Energy conversion efficiency (simple)

# TMP
#     def thermal_equalize(self, volume0, temp0, volume1, temp1):
#         TODO write the boiling thing
#         return (volume0*temp0 + volume1*temp1) / (volume0+volume1)

    def do_tick(self, water_in_separator, tick_time):
        # Heat exchanger SEPARATOR
        self.water_separator.heatexchanger(water_in_separator)

        # Calculate thermal flow of the water
        waterFlow_perTick = (self.waterflow_max * self.pump_performance) / tick_time

        self.water_separator.water_flow(waterFlow_perTick, self.water_pipe_before_separator)
        self.water_pipe_after_separator.water_flow(waterFlow_perTick, self.water_separator)

        # Turbine work TODO: more complex
        flow_energy = self.water_pipe_after_separator.water_flow_energy(waterFlow_perTick)
        self.water_pipe_after_separator.next_step_energy -= flow_energy
        working_energy = 0
        if flow_energy > 1500:
            working_energy = 120. / tick_time
        energy_MJ = working_energy * self.turbine_ece
        self.water_pipe_after_turbines.next_step_energy += (flow_energy - working_energy)

        # Heat exchanger CONDENSER
        # TODO: cooler
        self.water_pipe_before_separator.water_flow(waterFlow_perTick, self.water_pipe_after_turbines)
        # HACK
        self.water_pipe_before_separator.next_step_energy = self.water_pipe_before_separator.energy

        # Generator
        self.generator(energy_MJ, tick_time)

        # Steam pressure?
        # self.steam_pressure_hp_turbine = self.init_pressure + (ps.water_pipe_after_separator.temperature - self.init_temperature) * self.temperature_pressure_coeff

        # Update water energies
        all_water = [ self.water_separator, self.water_pipe_before_separator, self.water_pipe_after_separator,
                      self.water_pipe_after_turbines, self.water_cooler]
        for w in all_water:
            w.update_energies(self.pressure)

        print('2ND', self.water_separator.getTemperature(self.pressure), self.water_separator.amount)


    def generator(self, energy_of_turbine_MJ, tick_time):
        # Calc to Watt TODO: more complex
        self.power_output = energy_of_turbine_MJ * (tick_time)