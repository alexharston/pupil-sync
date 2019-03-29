import nidaqmx
import Task_Proxy

class BackgroundTick(Task_Proxy):

    def __init__(self, name, args=(), kwargs={'skipFirst': 0, 'skipFactor': 1}):
        logger.info('Starting PyTick background thread')
        super().__init__(name, None, args, kwargs)
        niTask = nidaqmx.Task()
		niTask.ao_channels.add_ao_voltage_chan('Dev1/ao1')
		self.niTask = niTask

    def _wrapper(self, pipe, _should_terminate_flag, generator, *args, **kwargs):
        while True:

            if pipe.poll(0):

                recvStr = pipe.recv()
                if recvStr == 'trigger':
                    try:
                        self.trigger(skipFirst, skipFactor)
                    except Exception as e:
                        pipe.send(e)
                        if not isinstance(e, EarlyCancellationError):
                            import traceback

                            logger.info(traceback.format_exc())
                        break
                
                elif recvStr == 'stopped':
                    break

                else:
                    logger.info('Invalid trigger received')
        
        pipe.close()
        logger.debug("Exiting _wrapper")

    def fetch(self):
        print('En Taro Tassadar!')

    def trigger(self, skipFirst, skipFactor):
        for _ in range(skipFirst + skipFactor):
            self.niTask.write([3.3], auto_start=True)
            time.sleep(0.002)
            self.niTask.write([0.0], auto_start=True)

    def finish(self, timeout=1):
        self.niTask.stop()
        if self.process is not None:
            self.process.join(timeout)
            self.process = None