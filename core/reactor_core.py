import core.smooth_step
import numpy as np
from core.water import Water

class Reactor_core:
    def __init__(self):
        # Changeable
        self.controlling_rods = 1. # percent
        self.pump_performance = 1. # percent

        # Observable
        self.fuel = 10 # mol
        self.poison = 0 # mol
        self.water_reactor = Water(100) # m3
        self.water_pipe_before_reactor = Water(1) # m3
        self.water_pipe_after_reactor = Water(1) # m3
        self.water_separator = Water(2) # m3

        self.pressure = Water.init_pressure
        self.n_emitor = 100 # neutron / sec

        # Hidden parameters/constants
        self.fission_probability = .9 # probability of a free neutron makes a fission
        self.poisonous_fission_probability = 0.1
        self.free_n = 0 # free neutrons
        self.controlling_rod_efficiency = .75 # efficiency percent
        self.waterflow_max = 1  # m3/sec
        self.free_n_of_fission = 3 # 2.5-3
        self.fissionEnergy = 200 # MeV                      todo multiple fission
        self.prompt_neutron_liftime_avg = 1e-4 # s
        self.poison_half_time = 1 * 60 # s
        self.poison_burn_temperature = 273 + 250 # K


    def MeV2MJ(self, MeV):
        return 1.6e-19 * MeV

    def numToMol(self, num):
        return num / 6.02214076e23 # Avogadro

    def fuel_heat_reactivity(self, avg_temperature):
        MAX_ACTIVITY = 1.   # constant
        MIN_ACTIVITY = 0.7  # constant
        MIN_TEMPERATURE = 273 + 200
        MAX_TEMPERATURE = 273 + 700
        val01 = core.smooth_step.smoothstep(avg_temperature, x_min=MIN_TEMPERATURE, x_max=MAX_TEMPERATURE)
        retVal = ((1.-val01) * (MAX_ACTIVITY-MIN_ACTIVITY)) + MIN_ACTIVITY
        return retVal

    def positive_void_coefficient(self, pressure):
        return 1. + self.water_reactor.getSteam(pressure) * .1

    def negative_water_coefficient(self):
        return 1.

    def poison_in_reactor(self):
        return 1. - (np.clip(self.poison / self.fuel, 0, 1))

    def new_fissions(self, pressure, tick_time):
        fuel_reactivity = 1. # init
        # Increase
        fuel_reactivity *= self.positive_void_coefficient(pressure)
        #Decrease
        fuel_reactivity *= self.negative_water_coefficient()
        fuel_reactivity *= self.fission_probability # geometry
        fuel_reactivity *= self.fuel_heat_reactivity(self.water_reactor.getTemperature(pressure))
        fuel_reactivity *= self.poison_in_reactor()

        # New free neutrons
        controlling_rod_modifier = 1. - (self.controlling_rods * self.controlling_rod_efficiency)
        neutrons = self.free_n + (self.n_emitor / tick_time)
        numOfFissions = 0
        # iteration = int(1./self.prompt_neutron_liftime_avg/self.tick_time)
        iteration = 1 # hack
        for i in range(0,iteration):
            actFissions = neutrons * fuel_reactivity * controlling_rod_modifier
            self.poison += self.numToMol(actFissions * self.poisonous_fission_probability)
            numOfFissions += actFissions
            neutrons = actFissions * self.free_n_of_fission
        self.free_n = neutrons

        # Poision decrease
        self.poison -= self.poison * 0.5 * ((1. / tick_time) / self.poison_half_time)
        current_temperature = self.water_reactor.getTemperature(pressure)
        if current_temperature > self.poison_burn_temperature:
            self.poison /= 2. # TODO make same graph?

        print('free neutrons', self.free_n, 'fissions', numOfFissions, 'poison', self.poison)

        # Produced thermal energy
        return numOfFissions * self.fissionEnergy


    def calculate_pressure(self, waters):
        p = 0
        s = 0
        for w in waters:
            p += w.calculate_pressure() * w.amount
            s += w.amount
        return p / s

    def chain_reaction(self, steam_circuit, cooling_circuit, tick_time):
        # Produced energy by reactor
        produced_thermal_energy = self.new_fissions(pressure=self.pressure, tick_time=tick_time) # MeV
        self.water_reactor.next_step_energy += self.MeV2MJ(produced_thermal_energy)

        # Calculate thermal flow of the water
        waterFlow_perTick = (self.waterflow_max * self.pump_performance) / tick_time
        self.water_reactor.water_flow(waterFlow_perTick, self.water_pipe_before_reactor)
        self.water_reactor.next_step_energy += self.MeV2MJ(MeV=produced_thermal_energy)
        self.water_pipe_after_reactor.water_flow(waterFlow_perTick, self.water_reactor)
        self.water_separator.water_flow(waterFlow_perTick, self.water_pipe_after_reactor)
        self.water_pipe_before_reactor.water_flow(waterFlow_perTick, self.water_separator)


        # Separator
        steam_circuit.do_tick(self.water_separator, cooling_circuit, tick_time) ###

        # Update water energies
        all_water = [self.water_reactor, self.water_pipe_before_reactor, self.water_pipe_after_reactor, self.water_separator]
        for w in all_water:
            w.update_energies(self.pressure)

        # Pressure chamber
        # todo?

        # Calculate pressure
        self.pressure = self.calculate_pressure(all_water)


        print('CORE',self.water_separator.getTemperature(self.pressure)-273)