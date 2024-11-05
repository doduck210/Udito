import gi
import sys, queue, threading, time
import numpy as np
import lkfs
from PyQt5 import QtWidgets, QtCore
from QTDesigner.MainWindow import Ui_MainWindow  
gi.require_version("Gst", "1.0")
from gi.repository import Gst

class GStreamerApp:
    def __init__(self):
        self.q = queue.Queue()
        self.q_flush = True
        self.meter = lkfs.Meter(48000)
        self.block = np.empty((0, 2))
        self.pipeline = None
        self.ui = None

    def get_buffer(self, name):
        sink = self.pipeline.get_by_name(name)
        pad = sink.pads[0]
        caps = pad.get_current_caps()
        struct = caps.get_structure(0)
        sample = sink.emit('pull-sample')
        buf = sample.get_buffer()
        mem = buf.get_all_memory()
        ret, mi = mem.map(Gst.MapFlags.READ)

        wavenp = np.frombuffer(mi.data, 'int32')  # Decklink audio, S32LE
        wavenp16 = (wavenp >> 16).astype('int16')
        mi.memory.unmap(mi)
        return wavenp16

    def on_new_buffer(self, sink):
        self.q.put(self.get_buffer("audiosink"))
        return Gst.FlowReturn.OK

    def lkfs_cal(self):
        self.q_flush = False
        result = self.q.get()
        chL = result[0::8]
        chR = result[1::8]
        samples = np.column_stack((chL, chR))
        samples = samples / 32768.0  # -1과 1사이 값으로
        self.block = np.vstack((self.block, samples))

        if self.block.shape[0] >= 19200:
            mlkfs = self.meter.mlkfs(self.block)
            print(mlkfs)
            if mlkfs>-10:
                mlkfs=-10
            elif mlkfs<-40:
                mlkfs=-40
            self.ui.update_progress(mlkfs)
            self.block = self.block[4800:]

        self.q_flush = True

    def start(self):
        pipe = "decklinkvideosrc ! fakesink decklinkaudiosrc channels=8 ! appsink name=audiosink"
        Gst.init()
        self.pipeline = Gst.parse_launch(pipe)

        sink = self.pipeline.get_by_name('audiosink')
        sink.set_property("emit-signals", True)
        sink.connect("new-sample", self.on_new_buffer)

        self.pipeline.set_state(Gst.State.READY)
        self.pipeline.set_state(Gst.State.PLAYING)

        bus = self.pipeline.get_bus()
        message = bus.timed_pop_filtered(5 * Gst.MSECOND, Gst.MessageType.ANY)

        try:
            while True:
                while (self.q.qsize() > 1 and self.q_flush):
                    threading.Thread(target=self.lkfs_cal).start()
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("keyboard interrupt..")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    gstreamer_app = GStreamerApp()
    gstreamer_app.ui = Ui_MainWindow()
    gstreamer_app.ui.setupUi(MainWindow)
    MainWindow.show()

    gstreamer_thread = threading.Thread(target=gstreamer_app.start)
    gstreamer_thread.start()

    sys.exit(app.exec_())
