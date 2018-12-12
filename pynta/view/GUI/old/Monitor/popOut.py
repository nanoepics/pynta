"""
    UUTrack.View.Monitor.popOut.py
    ===================================
    Pop-out window that can show predefined messages

    .. sectionauthor:: Sanli Faez <s.faez@uu.nl>
"""

from pyqtgraph.Qt import QtGui

class popOutWindow(QtGui.QWidget):
    """
    Simple window that contains the message text.
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # General layout of the widget
        self.layout = QtGui.QVBoxLayout(self)

        # Displays a textbox to the user with either information or a simple log.
        self.message = QtGui.QTextEdit()
        self.layout.addWidget(self.message)
        self.setupStyles()
        self.setupMessage()


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
        messagetitle = "UUTrack Assistant"
        shortcuts = """
                    F1, Show cheatsheet<br>
                    F5, Snap image<br>
                    F6, Continuous run<br>
                    Alt+mouse: Select line <br>
                    Ctrl+mouse: Crosshair <br>
                    Ctrl+B: Toggle buffering<br>
                    Ctrl+G: Toggle background subtraction<br>
                    Ctrl+F: Empty buffer<br>
                    Ctrl+C: Start tracking<br>
                    Ctrl+V: Stop tracking<br>
                    Ctrl+M: Autosave on<br>
                    Ctrl+N: Autosave off<br>
                    Ctrl+S: Save image<br>
                    Ctrl+W: Start waterfall<br>
                    Ctrl+Q: Exit application<br>
                    Ctrl+Shift+W: Save waterfall data<br>
                    Ctrl+Shift+T: Save trajectory<br>
                    """
        self.message.setHtml('<h1>%s</h1>%s' % (messagetitle, shortcuts))
