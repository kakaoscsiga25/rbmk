from core.water import Water
from core.generator import Generator

class Reactor_steam_circuit:
    def __init__(self):
        self.generator = Generator

        # Changeable
        self.pump_performance = 1. # percent

        # Observable
        self.water_separator = Water(2)
        self.water_pipe_after_separator = Water(1)
        self.water_pipe_after_turbines = Water(1)
        self.water_cooler = Water(2)
        self.water_pipe_before_separator = Water(1)

        self.waterflow_max = 1 # m3/s
        self.pressure_high = Water.init_pressure
        self.pressure_low = Water.init_pressure



    def calculate_pressure(self, waters):
        p = 0
        s = 0
        for w in waters:
            p += w.calculate_pressure() * w.amount
            s += w.amount
        return p / s


    def do_tick(self, water_in_separator, cooling_circuit, tick_time):
        # Heat exchanger SEPARATOR
        self.water_separator.heatexchanger(water_in_separator)

        # Calculate thermal flow of the water
        waterFlow_perTick = (self.waterflow_max * self.pump_performance) / tick_time

        self.water_separator.water_flow(waterFlow_perTick, self.water_pipe_before_separator)
        self.water_pipe_after_separator.water_flow(waterFlow_perTick, self.water_separator)

        # Turbine work TODO: more complex
        turbine_steam = Water(waterFlow_perTick, tick_time)
        turbine_steam.energy = self.water_pipe_after_separator.energy * min(1, self.water_pipe_after_separator.amount / turbine_steam.amount)
        self.generator.do_tick(turbine_steam=turbine_steam)

        self.water_pipe_after_separator.next_step_energy -= turbine_steam.energy
        self.water_pipe_after_turbines.next_step_energy += turbine_steam.next_step_energy

        self.water_cooler.water_flow(waterFlow_perTick, self.water_pipe_after_turbines)

        # Heat exchanger CONDENSER
        cooling_circuit.do_tick(self.water_cooler, tick_time)

        self.water_pipe_before_separator.water_flow(waterFlow_perTick, self.water_cooler)

        # Update water energies
        high_water = [ self.water_separator, self.water_pipe_after_separator]
        low_water = [ self.water_pipe_before_separator, self.water_pipe_after_turbines, self.water_cooler]
        for w in high_water:
            w.update_energies(self.pressure_high)
        for w in low_water:
            w.update_energies(self.pressure_low)

        # Calculate pressures
        self.pressure_high = self.calculate_pressure([self.water_separator, self.water_pipe_after_separator])
        # Low pressure is default (1e5)


        print('2ND', self.water_separator.getTemperature(self.pressure_high), self.water_separator.amount)

