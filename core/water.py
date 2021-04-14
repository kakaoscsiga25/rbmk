import numpy as np
#from core.reactor import Reactor
from decimal import Decimal

class Water:
    init_temperature = 273 + 24
    init_pressure = 1e5

    def __init__(self, amount, temperature = init_temperature):
        self.amount = amount            # m3

        self.water_heat_capacity = 4.2  # MJ/(1000kg*K)      todo graph
        self.steam_heat_capacity = 2.  # MJ/(1000kg*K)       todo graph
        self.water_boiling_energy = 2256.37 # MJ/m3
        self.temperature_pressure_coeff = 2.6e4  # Pascal/K  todo more precise solution

        self.energy = self.amount * temperature * self.water_heat_capacity # MJ
        self.next_step_energy = self.energy


    def getTemperature(self, pressure):
        boiling_point = self.calculate_boiling_point(pressure)
        [temperature, steam] = self.calculate_temperature_and_steam(boiling_point)
        return temperature

    def calculate_boiling_point(self, pressure):
        return np.log(pressure / 1e5) * 50 + 100 + 273

    def calculate_energy(self, boiling_point, amount):
        if self.steam_ratio == 0.:
            energy = amount * (self.temperature-self.init_temperature) * self.water_heat_capacity
        else:
            energy = amount * (boiling_point - self.init_temperature) * self.water_heat_capacity
            energy += (amount*self.steam_ratio) * self.water_boiling_energy
            if self.steam_ratio == 1.:
                energy += amount * (self.temperature-boiling_point) * self.steam_heat_capacity
        return energy

    def set_to_this_energy(self, energy, boiling_point):
        energy_to_boilingPoint = self.amount * (boiling_point-self.init_temperature) * self.water_heat_capacity
        if energy > energy_to_boilingPoint:
            self.temperature = boiling_point
            energy_boiling = self.amount * self.water_boiling_energy
            if energy > energy_to_boilingPoint + energy_boiling:
                self.temperature += (energy - energy_to_boilingPoint - energy_boiling) / (self.steam_heat_capacity*self.amount)
                self.steam_ratio = 1.
            else:
                self.steam_ratio = (energy - energy_to_boilingPoint) / (self.amount * self.water_boiling_energy)
        else:
            self.temperature = self.init_temperature + (energy / (self.water_heat_capacity*self.amount))
            self.steam_ratio = 0.

    def update(self, pressure):
        boiling_point = self.calculate_boiling_point(pressure)
        energy_to_boilingPoint = self.amount * boiling_point * self.water_heat_capacity
        if self.energy > energy_to_boilingPoint:
            self.temperature = boiling_point
            energy_boiling = self.amount * self.water_boiling_energy
            if self.energy > energy_to_boilingPoint + energy_boiling:
                self.temperature += (self.energy - energy_to_boilingPoint - energy_boiling) / (
                        self.steam_heat_capacity * self.amount)
                self.steam_ratio = 1.
            else:
                self.steam_ratio = (self.energy - energy_to_boilingPoint) / (self.amount * self.water_boiling_energy)
        else:
            self.temperature = (self.energy / (self.water_heat_capacity * self.amount))
            self.steam_ratio = 0.

    def calculate_temperature_and_steam(self, boiling_point):
        energy_to_boilingPoint = self.amount * boiling_point * self.water_heat_capacity
        if self.energy > energy_to_boilingPoint:
            temperature = boiling_point
            energy_boiling = self.amount * self.water_boiling_energy
            if self.energy > energy_to_boilingPoint + energy_boiling:
                temperature += (self.energy - energy_to_boilingPoint - energy_boiling) / (
                        self.steam_heat_capacity * self.amount)
                steam_ratio = 1.
            else:
                steam_ratio = (self.energy - energy_to_boilingPoint) / (self.amount * self.water_boiling_energy)
        else:
            temperature = (self.energy / (self.water_heat_capacity * self.amount))
            steam_ratio = 0.
        return [temperature, steam_ratio]

    def calculate_pressure(self):
        # Iteratively
        pressure = self.init_pressure
        preTemp = -999
        while (True):
            boiling_point = self.calculate_boiling_point(pressure)
            [temperature, steam] = self.calculate_temperature_and_steam(boiling_point)
            if temperature < boiling_point:
                break
            if abs(preTemp-temperature) > 0.5:
                preTemp = temperature
            else:
                break
        return self.init_pressure + (temperature - self.init_temperature) * self.temperature_pressure_coeff

    def water_flow_energy(self, flowAmount, flowSource = None):
        if flowSource is None:
            flowSource = self
        ratio = flowAmount / flowSource.amount
        ratio = min(ratio, 1.)
        return flowSource.energy * ratio  # MJ
    def water_flow(self, flowAmount, flowSourceWater):
        flow_energy = self.water_flow_energy(flowAmount, flowSourceWater)
        flowSourceWater.next_step_energy -= flow_energy
        self.next_step_energy += flow_energy

    def update_energies(self, pressure):
        # Update params
        self.energy = self.next_step_energy

    def heatexchanger(self, oWater):
        # TODO: efficiency
        new_energy = (self.energy + oWater.energy) / 2. # HACKY
        self.next_step_energy += new_energy - self.energy
        oWater.next_step_energy += new_energy - oWater.energy