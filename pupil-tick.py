from plugin import Plugin
import os
import sys
from time import time
import logging
import zmq
from pyglui import ui
from time import time
#import NI module

class PyTick(Plugin):
	icon_chr = "'"
	icon_font="roboto"

	def __init__(self, g_pool):
		super().__init__(g_pool)

		self.uniqueness = "by_class"
		self.order = 1

		self.count = 0
		self.start = None

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

