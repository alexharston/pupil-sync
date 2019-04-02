from BackgroundTick import BackgroundTick
from plugin import Plugin
from pyglui import ui
import os
import sys
import logging
#import NI module

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

        def cleanup(self):
            self.proxy.pipe.send('stopped')
            self.proxy.finish()

