import copy
import core.smooth_step
import numpy as np
from core.water import Water

class Reactor_core:
    def __init__(self):
        self.init_pressure = 1e5  # Pascal (N/m2)
        self.init_temperature = 273 + 24
        self.water_heat_capacity = 4.2  # MJ/(1000kg*K)      todo graph
        self.steam_heat_capacity = 2.  # MJ/(1000kg*K)       todo graph

        # Changeable
        self.controlling_rods = 1. # percent
        self.pump_performance = 1. # percent

        # Observable
        # self.fuel = 10 # mol
        # self.poison = 0 # mol
        self.water_reactor = Water(10) # m3
        self.water_pipe_before_reactor = Water(1) # m3
        self.water_pipe_after_reactor = Water(1) # m3
        self.water_separator = Water(2) # m3

        #self.temperature_water_reactor = 273 + 24
        #self.temperature_after_reactor = 273 + 24
        #self.temperature_before_reactor = 273 + 24
        #self.temperature_water_separator = 273 + 24
        #self.water_in_reactor = 10 # m3
        #self.water_in_pipe_before_reactor = 1 # m3
        #self.water_in_pipe_after_reactor = 1 # m3
        #self.water_in_separator = 2 # m3


        self.pressure = self.init_pressure
        self.n_emitor = 100 # neutron / sec

        # Hidden parameters/constants
        self.fission_probability = .9 # probability of a free neutron makes a fission
        self.free_n = 0 # free neutrons
        self.controlling_rod_efficiency = .75 # efficiency percent
        self.waterflow_max = 1  # m3/sec
        self.free_n_of_fission = 3 # 2.5-3
        self.fissionEnergy = 200 # MeV                      todo multiple fission
        self.steam_in_reactor_core = 0. # % steam in the core
        self.water_boiling_energy = 2256.37 # MJ/m3
        self.prompt_neutron_liftime_avg = 1e-4 # s



    def MeV2MJ(self, MeV):
        return 1.6e-19 * MeV

    def fuel_heat_reactivity(self, avg_temperature):
        MAX_ACTIVITY = 1.   # constant
        MIN_ACTIVITY = 0.7  # constant
        MIN_TEMPERATURE = 273 + 200
        MAX_TEMPERATURE = 273 + 700
        val01 = core.smooth_step.smoothstep(avg_temperature, x_min=MIN_TEMPERATURE, x_max=MAX_TEMPERATURE)
        # print('smooth', val, val01)
        # val01 = (val + np.pi/2) / np.pi
        retVal = ((1.-val01) * (MAX_ACTIVITY-MIN_ACTIVITY)) + MIN_ACTIVITY
        return retVal

    def positive_void_coefficient(self):
        return 1. + self.steam_in_reactor_core * .1

    def negative_water_coefficient(self):
        return 1.

    def new_fissions(self, pressure, tick_time):
        fuel_reactivity = 1. # init
        # Increase
        fuel_reactivity *= self.positive_void_coefficient()
        #Decrease
        fuel_reactivity *= self.negative_water_coefficient()
        fuel_reactivity *= self.fission_probability # geometry
        fuel_reactivity *= self.fuel_heat_reactivity(self.water_reactor.getTemperature(pressure))

        # New free neutrons
        controlling_rod_modifier = 1. - (self.controlling_rods * self.controlling_rod_efficiency)
        neutrons = self.free_n + (self.n_emitor / tick_time)
        numOfFissions = 0
        # iteration = int(1./self.prompt_neutron_liftime_avg/self.tick_time)
        iteration = 1 # hack
        for i in range(0,iteration):
            actFissions = neutrons * fuel_reactivity * controlling_rod_modifier
            numOfFissions += actFissions
            neutrons = actFissions * self.free_n_of_fission
        self.free_n = neutrons

        print('free neutrons', self.free_n, 'fissions', numOfFissions)

        # Produced thermal energy
        return numOfFissions * self.fissionEnergy

# TMP
    def calculate_boiling_point(self, pressure):
        return np.log(pressure / 1e5) * 50 + 100 + 273



    # def calculate_water_temperature_increase(self, energy, water_volume, waterTemperature):
    #     boiling_point = self.calculate_boiling_point(self.pressure)
    #     heat_increaser_energy = self.MeV2MJ(MeV=energy)
    #
    #     #hack todo: write me
    #     if (self.steam_in_reactor_core < 1.):
    #         waterTemperature = min(boiling_point, waterTemperature)
    #
    #     if (boiling_point < waterTemperature):
    #         return [(heat_increaser_energy / (self.steam_heat_capacity * water_volume)), 1.]
    #     energy_to_boiling = (boiling_point - waterTemperature) * self.water_heat_capacity * water_volume
    #     if energy_to_boiling < heat_increaser_energy:
    #         delta_energy = heat_increaser_energy - energy_to_boiling
    #         energy_to_boiling_all = self.water_boiling_energy * water_volume * (1. - self.steam_in_reactor_core)
    #         if delta_energy > energy_to_boiling_all:
    #             return [((delta_energy - energy_to_boiling_all) / (self.steam_heat_capacity * water_volume) + (boiling_point - waterTemperature)), 1.]
    #         else:
    #             return [(boiling_point-waterTemperature), (delta_energy / energy_to_boiling_all) + self.steam_in_reactor_core]
    #     else:
    #         return [(heat_increaser_energy / (self.water_heat_capacity * water_volume)), 0.]


    def calculate_pressure(self, waters):
        p = 0
        s = 0
        for w in waters:
            p += w.calculate_pressure() * w.amount
            s += w.amount
        return p / s

    def chain_reaction(self, steam_circuit, tick_time):
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

        # [temperature_diff, steam] = self.calculate_water_temperature_increase(produced_thermal_energy, ps.water_reactor.amount, ps.water_reactor.temperature)
        # self.water_reactor.temperature += temperature_diff
        # self.steam_in_reactor_core = steam

        # Separator
        steam_circuit.do_tick(self.water_separator, tick_time) ###

        all_water = [self.water_reactor, self.water_pipe_before_reactor, self.water_pipe_after_reactor, self.water_separator]
        # Calculate pressure
        self.pressure = self.calculate_pressure(all_water)


        # Pressure chamber
        # todo?

        # Update water energies
        for w in all_water:
            w.update_energies(self.pressure)

        print('CORE',self.water_separator.getTemperature(self.pressure)-273, self.calculate_boiling_point(self.pressure)-273, self.steam_in_reactor_core)