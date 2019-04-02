from plugin import Plugin
from ctypes import c_bool
from pyglui import ui
import os
import zmq
import sys
import time
import nidaqmx
import logging
import zmq_tools
import multiprocessing as mp

class PyTick(Plugin):
    icon_chr = "'"
    icon_font="roboto"

    def __init__(self, g_pool, skipFactor=1, skipFirst=0):
        super().__init__(g_pool)

        self.uniqueness = "by_class"
        self.order = 1

        self.state = 'stopped'
        self.proxy = BackgroundTick(
        'BackgroundTick', kwargs={'skipFactor': skipFactor, 'skipFirst':skipFirst})
        self.skipFactor = skipFactor
        self.skipFirst = skipFirst

    def init_ui(self):
        self.add_menu()
        self.menu.label = 'PyTick'
        help_str = "PyTick"
        self.menu.append(ui.Info_Text(help_str))
        # self.menu.append(ui.Text_Input('skipFactor'), self, label='Skip Factor')
        # self.menu.append(ui.Text_Input('skipFirst'), self, label='Skip First')

    def deinit_ui(self):
        self.remove_menu()


    def get_init_dict(self):
        return {'skipFactor': self.skipFactor, 'skipFirst': self.skipFirst}
    
    def on_char(self, character):
        if character is 's':
            if self.state == 'stopped':
                self.state = 'started'
                self.proxy.pipe.send('trigger')
            else:
                self.state = 'stopped'
                self.proxy.pipe.send('trigger')

    def on_notify(self, notification):
        # print(notification['subject'])
        if (notification['subject'] == 'recording.should_start') and self.state == 'stopped':
            self.state = 'started'
            self.proxy.pipe.send('trigger')
        elif notification['subject'] == 'recording.should_stop' and self.state == 'started':
            self.state = 'stopped'
            self.proxy.pipe.send('trigger')
        else:
            print(notification['subject'])

    def fetch(self):
        print('Fetched')

    def finish(self, timeout=1):
        self.niTask.stop()
        if self.process is not None:
            self.process.join(timeout)
            self.process = None
