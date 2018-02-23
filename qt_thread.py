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
    progress = pyqtSignal(int)
    status_camera = pyqtSignal(str)
    status_trigger = pyqtSignal(str)
    naming_error = pyqtSignal()
    name = pyqtSignal(str)
    colour = pyqtSignal(int, bool)
    roi = pyqtSignal(list, bool)


class Worker(QRunnable):
    """Worker thread that inherits from QRunnable to handle worker thread setup, signals and wrap-up"""

    def __init__(self, function, *args, **kwargs):

        super(Worker, self).__init__()

        # Store constructor arguments as instance variables that will be used when executing the function
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add any signal keywords to the kwargs here depending on the received function
        if 'run_processor' in str(function) or 'calibrate' in str(function) or 'convert_' in str(function):
            kwargs['status'] = self.signals.status
            kwargs['progress'] = self.signals.progress

        if 'calibrate' in str(function):
            kwargs['colour'] = self.signals.colour

        if 'convert_image' in str(function):
            kwargs['naming_error'] = self.signals.naming_error

        if 'capture_' in str(function):
            kwargs['status_camera'] = self.signals.status_camera
            kwargs['name'] = self.signals.name

        if 'capture_run' in str(function):
            kwargs['status_trigger'] = self.signals.status_trigger

        if 'draw_contours' in str(function):
            kwargs['roi'] = self.signals.roi

    @pyqtSlot()
    def run(self):
        """Initialize the runner function with the received args and kwargs"""

        try:
            result = self.function(*self.args, **self.kwargs)
        except:
            # Emit back an error if the function fails in any way
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Emit the result of the function
            self.signals.result.emit(result)
        finally:
            # Emit the done signal
            self.signals.finished.emit()