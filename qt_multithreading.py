# Import external libraries
import sys
import traceback
from PyQt5.QtCore import *


class WorkerSignals(QObject):
    """Signals available from a running worker thread are defined here"""
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    status = pyqtSignal(object)
    name = pyqtSignal(str)
    progress = pyqtSignal(int)
    colour = pyqtSignal(int, bool)


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
        if 'acquire_image' in str(self.function):
            kwargs['status'] = self.signals.status
            kwargs['name'] = self.signals.name

        if 'convert' in str(self.function) or 'detector' in str(self.function) or 'calibrate' in str(self.function):
            kwargs['status'] = self.signals.status
            kwargs['progress'] = self.signals.progress

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