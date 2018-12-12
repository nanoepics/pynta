"""
    UUTrack.View.Camera.messageWidget.py
    ====================================
    Simple widget that holds an HTML box to display messages to the user. Example of usage would be,

        >>> messageWidget.updateProcessor(psutil.cpu_percent())
        >>> msg = []
        >>> msg.append('<b>Error</b>: This is an error message.')
        >>> msg.append('<i>Info</i>: This is a test message.')
        >>> messageWidget.updateMessage(msg)

    The main objective of this widget is to confirm to the user that something was triggered and to have a permanent way of seeing it.

    .. todo:: This widget capabilities could be combined with some logging capabilities.

    .. todo:: Change colors for error, info and debug messages.

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""
from datetime import datetime
from pyqtgraph.Qt import QtGui

class messageWidget(QtGui.QWidget):
    """Widget that holds text boxes for displaying information to the user."""
    messageTitle = "Status"
    logTitle = "Log"
    logMaxLength = 20 # maximum length of the log to be displayed to the user.
    categories = {'i': 'Info',
                'e': 'Error',
                'w': 'Warning'}

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)

        # General layout of the widget
        self.layout = QtGui.QVBoxLayout(self)

        # Status bars to display memory and CPU usage to the user
        self.statusBars = QtGui.QHBoxLayout()
        self.memory = QtGui.QProgressBar(self)
        self.processor = QtGui.QProgressBar(self)
        self.statusBars.addWidget(self.memory)
        self.statusBars.addWidget(self.processor)

        # Displays a textbox to the user with either information or a simple log.
        self.message = QtGui.QTextEdit()
        self.log = QtGui.QTextEdit()


        self.layout.addLayout(self.statusBars)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.log)

        self.setupStyles()

        self.setupMessage()
        self.setupLog()

    def setupStyles(self):
        """ Setups three styles for the bars: Red, Yellow and Default. It is meant to be more graphical to the user regarding
        the availability of resources."""
        self.RED_STYLE = """
                QProgressBar{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center
                }

                QProgressBar::chunk {
                    background-color: red;
                    width: 10px;
                    margin: 1px;
                }
                """

        self.DEFAULT_STYLE = """
                QProgressBar{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center
                }

                QProgressBar::chunk {
                    background-color: green;
                    width: 10px;
                    margin: 1px;
                }
                """

        self.YELLOW_STYLE = """
                QProgressBar{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center
                }

                QProgressBar::chunk {
                    background-color: yellow;
                    width: 10px;
                    margin: 1px;
                }
                """

    def setupMessage(self):
        """Starts the message box with a title that will always be displayed."""
        self.message.setHtml('<h1>%s</h1>'%self.messageTitle)

    def updateMessage(self,msg):
        """Updates the message displayed to the user.

        :param msg: string or array, in which case every item will be displayed in a new line.
        :type msg: string or array.
        """
        message = '<h1>%s</h1>'%self.messageTitle
        if type(msg) == type([]):
            for m in msg:
                message += '<br/>%s'%m
        else:
            message += '<br/>%s'%msg

        self.message.setHtml(message)

    def setupLog(self):
        """Starts the log box with a title that will always be displayed on top."""
        self.log.setHtml('<h1>%s</h1>' % self.logTitle)
        self.logText = []

    def appendLog(self, cat, msg):
        """ Appends to the log the desired message.

        :param cat: Category of the message (i,w.e)
        :param msg: Message to display
        """
        c = self.categories[cat]
        t = datetime.now().strftime("%H:%M:%S")
        self.logText.append('%s  %s:  %s' % (t, c, msg))

        if len(self.logText)>self.logMaxLength:
            until = self.logMaxLength
        else:
            until = len(self.logText)

        message = ''
        mm = self.logText[-until:]
        for m in mm[::-1]:
            message += "<br />%s"%m
        self.log.setHtml(message)



    def updateLog(self,msg):
        """Updates the log displayed to the user by prepending the desired message to the available messages.

        :param msg: every item will be displayed in a new line
        :type msg: string or array."""
        message = '<h1>%s</h1>'%self.logTitle

        if type(msg) == type([]):
            for m in msg:
                self.logText.append(m)
        else:
            self.logText.append(msg)

        if len(self.logText)>self.logMaxLength:
            until = self.logMaxLength
        else:
            until = len(self.logText)

        mm = self.logText[-until:]
        for m in mm[::-1]:
            message += "<br />%s"%m
        self.log.setHtml(message)

    def updateMemory(self,percentage):
        """
        Updates the progress bar that displays how much memory is available to the user.

        :param percentage: Percentage of memory used.
        """
        if percentage > 75:
            self.memory.setStyleSheet(self.RED_STYLE)
        elif percentage > 50:
            self.memory.setStyleSheet(self.YELLOW_STYLE)
        else:
            self.memory.setStyleSheet(self.DEFAULT_STYLE)

        self.memory.setValue(percentage)

    def updateProcessor(self,percentage):
        """
        Updates the progress bar that displays how much of the processor is in use.

        :param percentage: Percentage of memory used.
        """
        if percentage > 75:
            self.processor.setStyleSheet(self.RED_STYLE)
        else:
            self.processor.setStyleSheet(self.DEFAULT_STYLE)

        self.processor.setValue(percentage)
