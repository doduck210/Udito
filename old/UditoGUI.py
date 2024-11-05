import gi, math, queue, threading, time, wave
import numpy as np
import lkfs
from PyQt5 import QtCore, QtGui, QtWidgets
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject
import sys

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(70, 40, 71, 231))
        self.progressBar.setMinimum(-50)
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", -24)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(QtCore.Qt.Vertical)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Udito"))

def get_buffer(name):
    global pipeline
    sink = pipeline.get_by_name(name)
    pad = sink.pads[0]
    caps=pad.get_current_caps()
    struct=caps.get_structure(0)
    #print(struct)
    rate = struct.get_int('rate')[1]
    format =  struct.get_string('format')
    channels = struct.get_int('channels')[1]
    layout = struct.get_string('layout')
    #print(rate, format, channels, layout)
    
    sample = sink.emit('pull-sample') 
    buf = sample.get_buffer()
    mem = buf.get_all_memory()
    ret, mi = mem.map(Gst.MapFlags.READ)
    #print(mem)
    wavenp = np.frombuffer(mi.data, 'int32')  # Decklink audio, S32LE
    wavenp16 = (wavenp >> 16).astype('int16')
    #print(wavenp16[:8])     # Shows First 8 channel audio data
    #print(np.sqrt(np.mean(wave**2)))
    mi.memory.unmap(mi)
    return wavenp16
    


def on_new_buffer(sink):
    global q
    #print(f'{sink}  arrived..')
    q.put(get_buffer("audiosink"))
    return Gst.FlowReturn.OK


def thread_write():
    global q, q_flush, block, meter
    q_flush = False
    
    result = q.get()
    #채널별 값
    chL=result[0::8]
    chR=result[1::8]
    samples=np.column_stack((chL,chR))
    samples=samples/32768.0 # -1과 1사이 값으로
    block=np.vstack((block,samples))
    
    if block.shape[0] >= 19200:
        mlkfs=meter.mlkfs(block)
        print(mlkfs)
        update_progress_bar(int(mlkfs))
        block=block[4800:]

    q_flush = True

def update_progress_bar(value):
    # Updating the progress bar in the GUI
    global ui
    ui.progressBar.setValue(value)

def run_gstreamer():
    global q, q_flush,meter,  block, pipeline
    q = queue.Queue()
    q_flush = True
    meter = lkfs.Meter(48000)
    block=np.empty((0,2))

    pipe = "decklinkvideosrc ! fakesink decklinkaudiosrc channels=8 ! appsink name=audiosink"
    Gst.init()
    pipeline = Gst.parse_launch(pipe)

    sink=pipeline.get_by_name('audiosink')
    #sink.set_property("max-buffers",100)
    sink.set_property("emit-signals", True)

    sink.connect("new-sample", on_new_buffer) 

    pipeline.set_state(Gst.State.READY)
    pipeline.set_state(Gst.State.PLAYING)


    bus = pipeline.get_bus()
    message = bus.timed_pop_filtered(5*Gst.MSECOND,Gst.MessageType.ANY)

    try:
        while True:
            print('qsize = ', q.qsize(), end="\r", flush=True)
            if (message.type != Gst.MessageType.STATE_CHANGED):
                print(message.type, message.src)
            while ((q.qsize() > 1) and q_flush):
                threading.Thread(target=thread_write).start()
                #time.sleep(0.1)
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("keyboard interrupt..")

if __name__ == "__main__":
    global ui
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    gstreamer_thread = threading.Thread(target=run_gstreamer)
    gstreamer_thread.start()
    sys.exit(app.exec_())
    
