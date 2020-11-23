import zmq
import pyaudio
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
import sys 

class Window(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        self.setWindowTitle("Python") 
        width = 750
        self.setFixedWidth(width) 
        self.setFixedHeight(500)
        self.label = QLabel("Simple Audio Player", self) 
        self.label.move(0, 0) 
        self.label.resize(120, 80) 

        self.button = QPushButton('Button', self)
        self.button.setToolTip('Play')
        self.button.move(100, 100) 
        self.button.move(100,70)
        self.button.clicked.connect(self.on_click)

        self.show() 

    
    def on_click(self):
        context = zmq.Context()
        print("Connecting to the server…")
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://localhost:5555")
        socket.subscribe("")

        sampleWidth = 2 # Just for example, get from metadata.
        nChannels = 2 # Just for example, get from metadata.
        frameRate = 44100 # Just for example, get from metadata.

        pAudio = pyaudio.PyAudio()
        stream = pAudio.open(
            format=pAudio.get_format_from_width(sampleWidth),
            channels=nChannels,
            rate=frameRate,
            output=True,
        )
        for request in range(10):
            message = socket.recv()

            stream.write(message)
            print("Received %sth " % (request))

if __name__=='__main__':

    app = QApplication(sys.argv)
    window = Window() 
    app.exec()
