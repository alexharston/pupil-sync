from plugin import Plugin
from pyglui import ui
from time import time
import os
import sys
import logging
#import NI module
import nidaqmx

class PyTick(Plugin):
	icon_chr = "'"
	icon_font="roboto"

	def __init__(self, g_pool):
		super().__init__(g_pool)

		self.uniqueness = "by_class"
		self.order = 1

		self.count = 0
		self.state = 'stopped'
		niTask = nidaqmx.Task()
		niTask.ao_channels.add_ao_voltage_chan('Dev1/ao1')
		self.niTask = niTask

	def init_ui(self):
		self.add_menu()
		self.menu.label = 'PyTick'
		help_str = "PyTick"
		self.menu.append(ui.Info_Text(help_str))

	def deinit_ui(self):
		self.remove_menu()


	def get_init_dict(self):
		return {}

	def on_notify(self, notification):
                print(notification['subject'])
                if notification['subject'] == 'recording.should_start' and self.state == 'stopped':
                        self.trigger()
                        self.state == 'started'
                elif notification['subject'] == 'recording.should_stop' and self.state == 'started':
                        self.trigger()
                        self.state = 'stopped'
                else:
                     print('Are you nut?!!!')   
        
        def trigger(self):
                self.niTask.write([3.3], auto_start=True)
                time.sleep(0.002)
                self.niTask.write([0.0], auto_start=True)

        def cleanup(self):
                self.niTask.stop()

