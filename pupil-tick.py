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

    def __init__(self, g_pool):
        super().__init__(g_pool)

        self.uniqueness = "by_class"
        self.order = 1

        self.state = 'stopped'
        self.proxy = BackgroundTick('BackgroundTick')
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

    def on_char(self, character):
        # print(character)
        if character == 's':
            # self.proxy.pipe.send('trigger')
            self.trigger(0,1)
            print('send trigger')

    def on_notify(self, notification):
        # print(notification['subject'])
        if notification['subject'] == 'recording.should_start' and self.state == 'stopped':
            self.state = 'started'
            self.trigger(1,1)
            # self.proxy.pipe.send('trigger')
        elif notification['subject'] == 'recording.should_stop' and self.state == 'started':
            self.state = 'stopped'
            self.trigger(1,1)
            # self.proxy.pipe.send('trigger')
        else:
            # print(sys.executable)
            # print('Error - if you are seeing this something has gone \
            #     pretty wrong.' )
            pass

    def trigger(self, skipFirst, skipFactor):
        # print('Sending trigger')
        for _ in range(skipFirst + skipFactor):
            self.niTask.write([3.3], auto_start=True)
            time.sleep(0.002)
            self.niTask.write([0.0], auto_start=True)
            time.sleep(0.001)
        # print('finish')

    def cleanup(self):
        self.proxy.pipe.send('stopped')
        self.proxy.finish()
        # pass

class EarlyCancellationError(Exception):
    pass
    
class BackgroundTick():

    def __init__(self, name, args=[], kwargs={'skipFirst': 0, 'skipFactor': 1}):
        self._should_terminate_flag = mp.Value(c_bool, 0)
        self._completed = False
        self._canceled = False

        pipe_recv, pipe_send = mp.Pipe(True)
        wrapper_args = self._prepare_wrapper_args(
            pipe_send, self._should_terminate_flag
        )
        wrapper_args.extend(args)
        self.process = mp.Process(
            target=self._wrapper, name=name, args=wrapper_args, kwargs=kwargs
        )
        self.process.daemon = True
        self.process.start()
        self.pipe = pipe_recv
        # logger.info('Starting PyTick background thread')
    
    def _prepare_wrapper_args(self, *args):
        return list(args)

    def _change_logging_behavior(self):
        pass

    def _wrapper(self, pipe, _should_terminate_flag, *args, **kwargs):
        
        niTask = nidaqmx.Task()
        niTask.ao_channels.add_ao_voltage_chan('Dev1/ao1')
        niTask.timing.cfg_samp_clk_timing(1000, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=2)

        def trigger(skipFirst, skipFactor):
            print('Sending trigger')
            for _ in range(skipFirst + skipFactor):
                niTask.write([3.3], auto_start=True)
                time.sleep(0.002)
                niTask.write([0.0], auto_start=True)
                time.sleep(0.001)
            print('finish')
        
        while True:

            if pipe.poll(0):
                recvStr = pipe.recv()
                print(recvStr)
                if recvStr == 'trigger':
                    try:
                        print('enter try block')
                        # trigger(0, 1)
                        niTask.write([3.3], auto_start=True)
                        # time.sleep(0.002)
                        niTask.write([0.0], auto_start=True)
                        # time.sleep(0.001)
                        
                    except Exception as e:
                        pipe.send(e)
                        if not isinstance(e, EarlyCancellationError):
                            import traceback

                            # logger.info(traceback.format_exc())
                        break
                
                elif recvStr == 'stopped':
                    break

                else:
                    # logger.info('Invalid trigger received')
                    pass
        
        pipe.close()
        # logger.debug("Exiting _wrapper")

    def fetch(self):
        print('Fetched')

    def finish(self, timeout=1):
        self.niTask.stop()
        if self.process is not None:
            self.process.join(timeout)
            self.process = None
