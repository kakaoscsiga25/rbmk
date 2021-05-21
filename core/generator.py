class Generator:
    def __init__(self):
        # Observables
        self.power_output = 0. # MW
        self.turbine_rpm = 0 # round/min

        # Constants
        self.generator_ece = 0.8  # Energy conversion efficiency (simple)
        self.turbine_ece = 0.2
        self.turbine_mass = 30 * 1000 # kg
        self.turbine_radius = 3 / 2. # m

    def generator(self, energy_of_turbine_MJ, tick_time):
        # Calc to Watt
        # TODO: more complex
        self.power_output = energy_of_turbine_MJ * (tick_time)

    def turbine_moment_of_inertia(self):
        return self.turbine_mass * self.turbine_radius * self.turbine_radius

    def do_tick(self, turbine_steam, tick_time):
        working_energy = 0
        if self.pressure_high > 15e5:
            working_energy = 120. / tick_time
        energy_MJ = working_energy * self.turbine_ece