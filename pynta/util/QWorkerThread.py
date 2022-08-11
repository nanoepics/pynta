from PyQt5 import QtCore
import traceback

class WorkThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        """
        When the WorkThread is called a function is being given to the class
        to run. Besides there is no limit of arguments that can be given with the given function.
        :param function: this is the function the thread is going to run.
        :param args: a way of notation to get any number of variables(with the *args)
        :param kwargs: a way of notation to get any number of variables(with the *kwargs)
        :param is_running: a parameter to see if the function is still running.
        """
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    # def run(self):
    #     self.function(*self.args,**self.kwargs)
    #     return

    # In order to prevent the gui from crashing on any crash in any thread, the execution is now wrapped in a try except.
    # If this turns out not te be desirable, switch back to the commented method above.
    def run(self):
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as e:
            print("error in thread:", str(e))
            traceback.print_exc()
