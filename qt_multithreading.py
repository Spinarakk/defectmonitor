# Import external libraries
import sys
import traceback
from PyQt5.QtCore import *


class WorkerSignals(QObject):
    """Signals available from a running worker thread are defined here"""

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

    status = pyqtSignal(str)
    status_camera = pyqtSignal(str)
    status_trigger = pyqtSignal(str)

    naming_error = pyqtSignal()

    name = pyqtSignal(str)
    progress = pyqtSignal(int)
    colour = pyqtSignal(int, bool)
    notification = pyqtSignal(str)


class Worker(QRunnable):
    """Worker thread that inherits from QRunnable to handle worker thread setup, signals and wrap-up"""

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments as instance variables that will be re-used for processing
        self.function = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add any signal keywords to the kwargs here depending on the sent function
        # acquire_image_snapshot / aquire_image_run
        if 'acquire_image' in str(self.function):
            kwargs['name'] = self.signals.name
            kwargs['status_camera'] = self.signals.status_camera
            if 'run' in str(self.function):
                kwargs['status_trigger'] = self.signals.status_trigger

        # convert_cli / convert_image_function / run_detector / calibrate
        if 'convert_' in str(self.function) or 'detector' in str(self.function) or 'calibrate' in str(self.function):
            kwargs['status'] = self.signals.status
            kwargs['progress'] = self.signals.progress

        # convert_image_function
        if 'convert_image_function' in str(self.function):
            kwargs['naming_error'] = self.signals.naming_error

        # run_detector
        if 'run_detector' in str(self.function):
            kwargs['notification'] = self.signals.notification

        # calibrate
        if 'calibrate' in str(self.function):
            kwargs['colour'] = self.signals.colour

    @pyqtSlot()
    def run(self):
        """Initialize the runner function with the received args and kwargs"""

        try:
            result = self.function(*self.args, **self.kwargs)
        except:
            # Emit back an error if the function fails in any way
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            #self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Emit the result of the function
            self.signals.result.emit(result)
        finally:
            # Emit the done signal
            self.signals.finished.emit()