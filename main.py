import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import threading
import time
import core.api as api

#fig, ax = plt.subplots()
#plt.subplots_adjust(left=0.25, bottom=0.25)

#import eel
#eel.init('frontend')
#eel.start('main_page.html', block=False)

def tick():
    while(run_tick):
        # Set changers
        api.set_controlling_rod(percent=controlling_rod.val)
        api.set_reactor_pump_performance(percent=reactor_pump_performance.val)
        api.set_steam_circuit_pump_performance(percent=second_circuit_pump_performance.val)

        api.do_tick()

        # Set observers
        temperature_before_reactor.set_val(api.get_temperature_water_before_reactor())
        temperature_in_reactor.set_val(api.get_temperature_water_reactor())
        temperature_after_reactor.set_val(api.get_temperature_water_after_reactor())
        temperature_in_separator.set_val(api.get_temperature_water_in_separator_core_circuit())
        steam_in_reactor.set_val(api.get_steam_in_reactor())
        pressure.set_val(api.get_pressure())

        temperature_in_separator2.set_val(api.get_temperature_water_in_separator_steam_circuit())
        temperature_water_after_separator.set_val(api.get_temperature_water_after_separator())
        temperature_water_after_turbines.set_val(api.get_temperature_water_after_turbines())
        temperature_water_before_separator.set_val(api.get_temperature_water_before_separator())
        power_output.set_val(api.get_output_power())

        time.sleep(1. / api.get_tick_time())

BAR_INIT_X = 0.35
BAR_INIT_WIDTH = 0.5
BAR_VERTICAL_SPACE = 0.05
BAR_HEIGHT = 0.03
BAR_Y = 0.9 # init

# Changers
controlling_rod = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='red'),
                         'Controlling rods', valmin=0., valmax=100.0, valinit=100, valstep=.1)
BAR_Y -= BAR_VERTICAL_SPACE
reactor_pump_performance = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='red'),
                         'Reactor pump performance', valmin=0., valmax=100.0, valinit=10, valstep=1)
BAR_Y -= BAR_VERTICAL_SPACE
second_circuit_pump_performance = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='red'),
                         'Second circuit pump performance', valmin=0., valmax=100.0, valinit=0, valstep=1)
BAR_Y -= BAR_VERTICAL_SPACE * 2

# Observers
########################### CORE ###########################
temperature_before_reactor = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'Water temperature before core', valmin=0, valmax=730, valstep=1, valfmt='%0.2f C')
temperature_before_reactor.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE
temperature_in_reactor = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'Water temperature in core', valmin=0, valmax=730, valstep=1, valfmt='%0.2f C')
temperature_in_reactor.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE
temperature_after_reactor = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'Water temperature after core', valmin=0, valmax=730, valstep=1, valfmt='%0.2f C')
temperature_after_reactor.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE
temperature_in_separator = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'Water temperature in separator', valmin=0, valmax=730, valstep=1, valfmt='%0.2f C')
temperature_in_separator.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE * 2


steam_in_reactor = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                  'Steam in reactor', valmin=0, valmax=100, valstep=1, valfmt='%0.1f %%')
steam_in_reactor.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE

pressure = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                  'Pressure', valmin=0, valmax=200, valstep=1, valfmt='%0.2f Bar')
pressure.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE * 2

########################### STEAM CIRCUIT ###########################
temperature_in_separator2 = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'Water temperature in separator2', valmin=0, valmax=730, valstep=1, valfmt='%0.2f C')
temperature_in_separator2.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE
temperature_water_after_separator = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'Water temperature after separator', valmin=0, valmax=730, valstep=1, valfmt='%0.2f C')
temperature_water_after_separator.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE
temperature_water_after_turbines = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'Water temperature after turbines', valmin=0, valmax=730, valstep=1, valfmt='%0.2f C')
temperature_water_after_turbines.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE
temperature_water_before_separator = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'Water temperature before separator2', valmin=0, valmax=730, valstep=1, valfmt='%0.2f C')
temperature_water_before_separator.set_active(False)
BAR_Y -= BAR_VERTICAL_SPACE * 2

power_output = Slider(plt.axes([BAR_INIT_X, BAR_Y, BAR_INIT_WIDTH, BAR_HEIGHT], facecolor='lightgoldenrodyellow'),
                                   'POWER OUTPUT', valmin=0, valmax=100, valstep=1, valfmt='%0.2f MW')
power_output.set_active(False)



run_tick = True
t = threading.Thread(target=tick, args=())
t.start()

plt.show()
run_tick = False
