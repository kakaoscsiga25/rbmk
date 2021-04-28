from core.water import Water


class Reactor_cooling:
    def __init__(self):
        # Changeable
        self.pump_performance = 1.
        # ?
        self.input_water_temperature = 24 + 273     # K

        # Observable
        self.output_water_temperature = self.input_water_temperature
        # Constants
        self.waterflow_max = 1 # m3/s
        self.pressure = Water.init_pressure


    def do_tick(self, steam_circuit_water, tick_time):
        # Calculate thermal flow of the water
        waterFlow_perTick = (self.waterflow_max * self.pump_performance) / tick_time

        water_river = Water(waterFlow_perTick, self.input_water_temperature)

        water_river.heatexchanger(steam_circuit_water)

        water_river.update_energies(self.pressure)
        self.output_water_temperature = water_river.getTemperature(self.pressure)
