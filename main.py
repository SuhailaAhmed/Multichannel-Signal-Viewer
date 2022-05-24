import matplotlib
from PyPDF2.pdf import PdfFileReader
from PyQt5 import QtCore, QtGui, QtWidgets

matplotlib.use("Qt5Agg")
import sys

import matplotlib.pyplot as plt
import pandas as pd
import pyqtgraph as pg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyPDF2 import PdfFileMerger
from PyQt5 import QtCore, QtGui, QtPrintSupport, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QSlider
from pyqtgraph import PlotWidget

sig_data = []


def print_widget(widget, pdf_filename):
    printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
    printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
    printer.setOutputFileName(pdf_filename)
    painter = QtGui.QPainter(printer)

    # start scale
    xscale = printer.pageRect().width() * 1.0 / widget.width()
    yscale = printer.pageRect().height() * 1.0 / widget.height()
    scale = min(xscale, yscale)
    painter.translate(printer.paperRect().center())
    painter.scale(scale, scale)
    painter.translate(-widget.width() / 2, -widget.height() / 2)
    # end scale

    widget.render(painter)
    painter.end()

    merger = PdfFileMerger()

    merger.append(PdfFileReader(open(pdf_filename, "rb")))
    merger.append(PdfFileReader(open(pdf_filename + ".pdf", "rb")))
    merger.write(pdf_filename)
    merger.close()


def table_creation(self, pdffilename):
    table_header = [
        "Signal Name",
        "Mean",
        "Standard Deviation",
        "Maximum Value",
        "Minimum Value",
        "duration",
    ]
    table_data = [table_header]

    # sig_info=[1,1,1,2,3]
    # sig_data=[data1]
    # if data2:
    # sig_data.append(data2)
    # if data3:
    # sig_data.append(data3)
    chn = [self.Channel_1.text(), self.Channel_2.text(), self.Channel_3.text()]
    i = 0
    for signal_data in sig_data:

        amp = signal_data[1]
        tim = signal_data[0]
        signal_info = [
            "{}".format(chn[i]),
            round(amp.mean(), 5),
            round(amp.std(), 5),
            round(amp.max(), 5),
            round(amp.min(), 5),
            round((tim.max() - tim.min()), 5),
        ]
        table_data.append(signal_info)
        i = i + 1
    fig = plt.figure(constrained_layout=True)
    fig.patch.set_visible(False)
    fig, ax = plt.subplots()
    ax.axis("off")
    ax.axis("tight")
    table = ax.table(cellText=table_data, loc="center")
    table.scale(1, 2)
    fig.tight_layout()
    file_name = pdffilename + ".pdf"
    report = PdfPages(file_name)
    report.savefig()
    plt.close
    report.close()


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set(
            xlabel="time (sec)",
            ylabel="frequency (Hz)",
        )
        # self.axes.grid()
        super(MplCanvas, self).__init__(fig)


class Canvas(FigureCanvas):
    def __init__(self, path, cmap, min, max):

        fig, self.ax = plt.subplots(figsize=(5, 4))
        super().__init__(fig)

        # self.setParent(parent)

        """ 
        Matplotlib Script
        """
        data = pd.read_csv(path, header=None)
        time = data[0]
        amplitude = data[1]
        fs = int(1 / 0.004)

        self.ax.specgram(
            amplitude, NFFT=1024, Fs=fs, noverlap=900, cmap=cmap, vmin=min, vmax=max
        )

        self.ax.set(
            xlabel="time (sec)",
            ylabel="frequency (Hz)",
        )
        self.ax.grid()


class Ui_MainWindow(object):
    def __init__(self):
        self.channel1 = False
        self.channel2 = False
        self.channel3 = False
        self.zoomIn_scale = 0.5
        self.zoomOut_scale = 2
        self.Interval = 1000
        self.myFig1 = None
        self.myFig2 = None
        self.myFig3 = None
        self.curr_spec_fig = 0
        self.curr_cmap = "viridis"
        self.curr_color = "blue"
        self.min = -100
        self.max = -50

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 573)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.splitter_Buttons = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_Buttons.setGeometry(QtCore.QRect(10, 500, 450, 23))
        self.splitter_Buttons.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_Buttons.setObjectName("splitter_Buttons")

        self.textbox = QLineEdit(self.centralwidget)
        self.textbox.move(930, 500)  # (590, 450, 41, 41)
        self.textbox.resize(60, 20)

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(900, 500, 20, 20))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("1")
        self.comboBox.addItem("2")
        self.comboBox.addItem("3")
        self.comboBox.currentIndexChanged.connect(
            lambda: self.rename_channel(self.comboBox.currentIndex())
        )

        self.Channel_inp = QtWidgets.QLabel(self.centralwidget)
        self.Channel_inp.setGeometry(QtCore.QRect(830, 500, 70, 20))
        self.Channel_inp.setTextFormat(QtCore.Qt.PlainText)

        self.pushButton_speedup = QtWidgets.QPushButton(self.splitter_Buttons)
        self.pushButton_speedup.setObjectName("pushButton_speedup")
        self.pushButton_speedup.clicked.connect(lambda: self.SpeedUp())
        self.pushButton_speeddown = QtWidgets.QPushButton(self.splitter_Buttons)
        self.pushButton_speeddown.setObjectName("pushButton_speeddown")

        self.pushButton_play = QtWidgets.QPushButton(self.splitter_Buttons)
        self.pushButton_play.setObjectName("pushButton_play")
        self.pushButton_play.clicked.connect(lambda: self.play(self.Interval))

        self.pushButton_stop = QtWidgets.QPushButton(self.splitter_Buttons)
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.pushButton_stop.clicked.connect(lambda: self.stopGraph())

        self.pushButton_zoomIn = QtWidgets.QPushButton(self.splitter_Buttons)
        self.pushButton_zoomIn.setObjectName("pushButton_zoomIn")
        self.pushButton_zoomIn.clicked.connect(lambda: self.zoom_in(self.zoomIn_scale))

        self.pushButton_zoomOut = QtWidgets.QPushButton(self.splitter_Buttons)
        self.pushButton_zoomOut.setObjectName("pushButton_zoomOut")
        self.pushButton_zoomOut.clicked.connect(
            lambda: self.zoom_out(self.zoomOut_scale)
        )

        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(100, 470, 281, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")  ############
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(10)
        self.horizontalSlider.setValue(0)
        self.horizontalSlider.setTickInterval(1)
        self.horizontalSlider.setTickPosition(QSlider.TicksBelow)
        self.horizontalSlider.valueChanged.connect(lambda: self.scroll_horizontal())

        self.splitter_show_hide = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_show_hide.setGeometry(QtCore.QRect(470, 440, 71, 81))
        self.splitter_show_hide.setOrientation(QtCore.Qt.Vertical)
        self.splitter_show_hide.setObjectName("splitter_show_hide")
        self.label_show_hide = QtWidgets.QLabel(self.splitter_show_hide)
        self.label_show_hide.setObjectName("label_show_hide")

        self.checkBox_Ch1 = QtWidgets.QCheckBox(self.splitter_show_hide)
        self.checkBox_Ch1.setObjectName("checkBox_Ch1")
        self.checkBox_Ch1.setChecked(True)
        self.checkBox_Ch1.stateChanged.connect(lambda: self.Show_Hide())

        self.checkBox_Ch2 = QtWidgets.QCheckBox(self.splitter_show_hide)
        self.checkBox_Ch2.setObjectName("checkBox_Ch2")
        self.checkBox_Ch2.setChecked(True)
        self.checkBox_Ch2.stateChanged.connect(lambda: self.Show_Hide())

        self.checkBox_Ch3 = QtWidgets.QCheckBox(self.splitter_show_hide)
        self.checkBox_Ch3.setObjectName("checkBox_Ch3")
        self.checkBox_Ch3.setChecked(True)
        self.checkBox_Ch3.stateChanged.connect(lambda: self.Show_Hide())

        self.splitter_labelsV = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_labelsV.setGeometry(QtCore.QRect(590, 450, 41, 41))
        self.splitter_labelsV.setOrientation(QtCore.Qt.Vertical)
        self.splitter_labelsV.setObjectName("splitter_labelsV")
        self.label_vmax = QtWidgets.QLabel(self.splitter_labelsV)
        self.label_vmax.setObjectName("label_vmax")
        self.label_vmin = QtWidgets.QLabel(self.splitter_labelsV)
        self.label_vmin.setObjectName("label_vmin")

        self.verticalSlider = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider.setGeometry(QtCore.QRect(950, 70, 22, 201))
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.verticalSlider.setMinimum(-1)
        self.verticalSlider.setMaximum(1)
        self.verticalSlider.setValue(0)
        self.verticalSlider.setTickInterval(1)
        self.verticalSlider.setTickPosition(QSlider.TicksBelow)
        self.verticalSlider.valueChanged.connect(lambda: self.scroll_vertical())

        self.splitter_channelNames = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_channelNames.setGeometry(QtCore.QRect(10, 20, 51, 461))
        self.splitter_channelNames.setOrientation(QtCore.Qt.Vertical)
        self.splitter_channelNames.setObjectName("splitter_channelNames")

        self.Channel_1 = QtWidgets.QLabel(self.splitter_channelNames)
        self.Channel_1.setTextFormat(QtCore.Qt.PlainText)
        self.Channel_1.setObjectName("Channel_1")

        self.Channel_2 = QtWidgets.QLabel(self.splitter_channelNames)
        self.Channel_2.setTextFormat(QtCore.Qt.PlainText)
        self.Channel_2.setObjectName("Channel_2")

        self.Channel_3 = QtWidgets.QLabel(self.splitter_channelNames)
        self.Channel_3.setTextFormat(QtCore.Qt.PlainText)
        self.Channel_3.setObjectName("Channel_3")

        self.splitter_vmin_vmax = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_vmin_vmax.setGeometry(QtCore.QRect(650, 450, 171, 44))
        self.splitter_vmin_vmax.setOrientation(QtCore.Qt.Vertical)
        self.splitter_vmin_vmax.setObjectName("splitter_vmin_vmax")

        self.vmax_slider = QtWidgets.QSlider(self.splitter_vmin_vmax)
        self.vmax_slider.setOrientation(QtCore.Qt.Horizontal)
        self.vmax_slider.setObjectName("vmax_slider")
        self.vmax_slider.setMinimum(-75)
        self.vmax_slider.setMaximum(-25)
        self.vmax_slider.setValue(-50)
        self.vmax_slider.setTickInterval(12)
        self.vmax_slider.setTickPosition(QSlider.TicksBelow)
        self.vmax_slider.valueChanged.connect(lambda: self.Contrast_max_change())

        self.vmin_slider = QtWidgets.QSlider(self.splitter_vmin_vmax)
        self.vmin_slider.setOrientation(QtCore.Qt.Horizontal)
        self.vmin_slider.setObjectName("vmin_slider")
        self.vmin_slider.setMinimum(-150)
        self.vmin_slider.setMaximum(-75)
        self.vmin_slider.setValue(-100)
        self.vmin_slider.setTickInterval(12)
        self.vmin_slider.setTickPosition(QSlider.TicksBelow)
        self.vmin_slider.valueChanged.connect(lambda: self.Contrast_min_change())

        self.splitter_foCombobox = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_foCombobox.setGeometry(QtCore.QRect(550, 500, 270, 20))
        self.splitter_foCombobox.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_foCombobox.setObjectName("splitter_foCombobox")

        color_palette = ["viridis", "plasma", "ocean", "nipy_spectral", "terrain"]
        self.comboBox_color = QtWidgets.QComboBox(self.splitter_foCombobox)
        self.comboBox_color.setObjectName("comboBox_color")
        for color in color_palette:
            self.comboBox_color.addItem(color)

        self.comboBox_color.currentIndexChanged.connect(
            lambda: self.Change_spectrogram_clr(self.comboBox_color.currentIndex())
        )

        # colorrrrrrr
        channel_no = ["Channel1", "Channel2", "Channel3"]
        self.comboBox_spectro = QtWidgets.QComboBox(self.splitter_foCombobox)
        self.comboBox_spectro.setObjectName("comboBox_spectro")
        for channel in channel_no:
            self.comboBox_spectro.addItem(channel)

        self.comboBox_spectro.currentIndexChanged.connect(
            lambda: self.open_spectrogram(self.comboBox_spectro.currentIndex())
        )

        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(70, 10, 530, 420))
        self.splitter.setOrientation(QtCore.Qt.Vertical)  # for graphs
        self.splitter.setObjectName("splitter")
        self.splitter.setHandleWidth(0)

        self.graphicsView = PlotWidget(self.splitter)
        self.graphicsView.setStyleSheet("background: rgb(255,255,255)")
        self.graphicsView.setObjectName("graphicsView")
        self.splitter.addWidget(self.graphicsView)
        self.graphicsView.getPlotItem().hideAxis("bottom")
        # self.graphicsView.hide()

        self.graphicsView_2 = PlotWidget(self.splitter)
        self.graphicsView_2.setStyleSheet("background: rgb(0,0,0)")
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.splitter.addWidget(self.graphicsView_2)
        self.graphicsView_2.getPlotItem().hideAxis("bottom")

        self.graphicsView_3 = PlotWidget(self.splitter)
        self.graphicsView_3.setStyleSheet("background: rgb(0,0,0)")
        self.graphicsView_3.setObjectName("graphicsView_3")
        self.splitter.addWidget(self.graphicsView_3)

        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(70, 10, 830, 420))
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter_2.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 861, 21))
        self.menubar.setObjectName("menubar")
        self.menufile = QtWidgets.QMenu(self.menubar)
        self.menufile.setObjectName("menufile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionopen = QtWidgets.QAction(MainWindow)
        self.actionopen.setObjectName("actionopen")
        self.actionopen.triggered.connect(lambda: self.Open_file())
        self.actionexport = QtWidgets.QAction(MainWindow)
        self.actionexport.setObjectName("actionExport")
        self.actionexport.triggered.connect(lambda: self.saving_pdf())

        self.menufile.addAction(self.actionopen)
        self.menufile.addAction(self.actionexport)
        self.menubar.addAction(self.menufile.menuAction())

        self.xmax_scale1 = 0.05
        self.xmin_scale1 = 0
        self.xmax_scale2 = 0.05
        self.xmin_scale2 = 0
        self.xmax_scale3 = 0.05
        self.xmin_scale3 = 0

        self.pen1 = pg.mkPen((0, 0, 255), width=0.5)

        self.x_range1 = self.graphicsView.getViewBox().state["viewRange"][0]
        self.x_range2 = self.graphicsView_2.getViewBox().state["viewRange"][0]
        self.x_range3 = self.graphicsView_3.getViewBox().state["viewRange"][0]

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_speedup.setText(_translate("MainWindow", "speedUp"))
        self.pushButton_speeddown.setText(_translate("MainWindow", "speedDown"))
        self.pushButton_play.setText(_translate("MainWindow", "play"))
        self.pushButton_stop.setText(_translate("MainWindow", "stop"))
        self.pushButton_zoomIn.setText(_translate("MainWindow", "zoomIn"))
        self.pushButton_zoomOut.setText(_translate("MainWindow", "zoomOut"))
        self.label_show_hide.setText(_translate("MainWindow", "Show/Hide"))
        self.checkBox_Ch1.setText(_translate("MainWindow", "Channel 1"))
        self.checkBox_Ch2.setText(_translate("MainWindow", "Channel 2"))
        self.checkBox_Ch3.setText(_translate("MainWindow", "Channel 3"))
        self.label_vmax.setText(_translate("MainWindow", "vmax"))
        self.label_vmin.setText(_translate("MainWindow", "vmin"))
        self.Channel_1.setText(_translate("MainWindow", "Channel 1"))
        self.Channel_2.setText(_translate("MainWindow", "Channel 2"))
        self.Channel_3.setText(_translate("MainWindow", "Channel 3"))
        self.Channel_inp.setText(_translate("MainWindow", "Channel No."))
        self.menufile.setTitle(_translate("MainWindow", "file"))
        self.actionopen.setText(_translate("MainWindow", "open"))
        self.actionexport.setText(_translate("MainWindow", "export"))

    def Contrast_max_change(self):
        self.max = self.vmax_slider.value()

        if self.curr_spec_fig == 1:
            self.myFig1.hide()
            self.myFig1 = Canvas(self.channel1_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig1)
        elif self.curr_spec_fig == 2:
            self.myFig2.hide()
            self.myFig2 = Canvas(self.channel2_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig2)
        elif self.curr_spec_fig == 3:
            self.myFig3.hide()
            self.myFig3 = Canvas(self.channel3_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig3)

    def Contrast_min_change(self):
        self.min = self.vmin_slider.value()

        if self.curr_spec_fig == 1:
            self.myFig1.hide()
            self.myFig1 = Canvas(self.channel1_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig1)
        elif self.curr_spec_fig == 2:
            self.myFig2.hide()
            self.myFig2 = Canvas(self.channel2_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig2)
        elif self.curr_spec_fig == 3:
            self.myFig3.hide()
            self.myFig3 = Canvas(self.channel3_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig3)

    def Change_spectrogram_clr(self, clr_idx):
        if clr_idx == 0:
            self.curr_cmap = "viridis"
            self.pen1 = pg.mkPen((0, 0, 255), width=0.5)
            # blue
        elif clr_idx == 1:
            self.curr_cmap = "plasma"  # orange
            self.pen1 = pg.mkPen((255, 165, 0), width=0.5)

        elif clr_idx == 2:
            self.curr_cmap = "ocean"  # navy
            self.curr_color = (0, 0, 128)
            self.pen1 = pg.mkPen((0, 0, 128), width=0.5)

        elif clr_idx == 3:
            self.curr_cmap = "nipy_spectral"  # green
            self.curr_color = (0, 255, 0)
            self.pen1 = pg.mkPen((0, 255, 0), width=0.5)

        elif clr_idx == 4:
            self.curr_cmap = "terrain"  # beige
            self.curr_color = (245, 245, 220)
            self.pen1 = pg.mkPen((245, 245, 220), width=0.5)

        if self.curr_spec_fig == 1:
            self.myFig1.hide()
            self.myFig1 = Canvas(self.channel1_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig1)
        elif self.curr_spec_fig == 2:
            self.myFig2.hide()
            self.myFig2 = Canvas(self.channel2_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig2)
        elif self.curr_spec_fig == 3:
            self.myFig3.hide()
            self.myFig3 = Canvas(self.channel3_path, self.curr_cmap, self.min, self.max)
            self.splitter_2.addWidget(self.myFig3)

    def open_spectrogram(self, channel_idx):
        if channel_idx == 0 and self.channel1 == True:
            self.myFig1 = Canvas(self.channel1_path, "viridis", self.min, self.max)
            self.curr_spec_fig = 1
            self.splitter_2.addWidget(self.myFig1)
            if self.myFig2 != None:
                self.myFig2.hide()
            if self.myFig3 != None:
                self.myFig3.hide()

        elif channel_idx == 0 and self.channel1 == False:
            sc = MplCanvas(self, width=5, height=4, dpi=100)
            sc.axes.plot([0], [0])
            # sc.set(xlabel='time (sec)', ylabel='frequency (Hz)', )
            self.splitter_2.addWidget(sc)
            # self.show()
            if self.myFig2 != None:
                self.myFig2.hide()
            if self.myFig3 != None:
                self.myFig3.hide()

        elif channel_idx == 1 and self.channel2 == True:
            self.myFig2 = Canvas(self.channel2_path, "viridis", self.min, self.max)
            self.curr_spec_fig = 2
            if self.myFig3 != None:
                self.myFig3.hide()
            if self.myFig1 != None:
                self.myFig1.hide()
            self.splitter_2.addWidget(self.myFig2)

        elif channel_idx == 1 and self.channel2 == False:
            sc = MplCanvas(self, width=5, height=4, dpi=100)
            sc.axes.plot([0], [0])
            # sc.set(xlabel='time (sec)', ylabel='frequency (Hz)', )
            self.splitter_2.addWidget(sc)
            # self.show()
            if self.myFig1 != None:
                self.myFig1.hide()
            if self.myFig3 != None:
                self.myFig3.hide()

        elif channel_idx == 2 and self.channel3 == True:
            self.myFig3 = Canvas(self.channel3_path, "viridis", self.min, self.max)
            self.curr_spec_fig = 3
            if self.myFig2 != None:
                self.myFig2.hide()
            if self.myFig1 != None:
                self.myFig1.hide()
            self.splitter_2.addWidget(self.myFig3)
        elif channel_idx == 2 and self.channel3 == False:
            sc = MplCanvas(self, width=5, height=4, dpi=100)
            sc.axes.plot([0], [0])
            # sc.set(xlabel='time (sec)', ylabel='frequency (Hz)', )
            self.splitter_2.addWidget(sc)
            # self.show()
            if self.myFig1 != None:
                self.myFig1.hide()
            if self.myFig2 != None:
                self.myFig2.hide()

    def rename_channel(self, channelidx):
        _translate = QtCore.QCoreApplication.translate
        if channelidx == 0:
            name1 = self.Channel_1.setText(
                _translate("MainWindow", self.textbox.text())
            )
            name1
        elif channelidx == 1:
            self.Channel_2.setText(_translate("MainWindow", self.textbox.text()))
        elif channelidx == 2:
            self.Channel_3.setText(_translate("MainWindow", self.textbox.text()))

    def Show_Hide(self):
        if self.checkBox_Ch1.isChecked():
            self.graphicsView.show()
            self.Channel_1.show()
        else:
            self.graphicsView.hide()
            self.Channel_1.hide()

        if self.checkBox_Ch2.isChecked():
            self.graphicsView_2.show()
            self.Channel_2.show()
            self.graphicsView.getPlotItem().hideAxis("bottom")
        else:
            self.graphicsView_2.hide()
            self.Channel_2.hide()
            if self.checkBox_Ch3.isChecked() == False:
                self.graphicsView.getPlotItem().showAxis("bottom")

        if self.checkBox_Ch3.isChecked():
            self.graphicsView_3.show()
            self.graphicsView_2.getPlotItem().hideAxis("bottom")
            self.Channel_3.show()
        else:
            self.graphicsView_3.hide()
            self.Channel_3.hide()
            self.graphicsView_2.getPlotItem().showAxis("bottom")

    def scroll_vertical(self):
        value = self.verticalSlider.value()
        if self.channel3 == True:
            self.timer1.stop()
            y1 = max(data1)
            self.y_range11 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.y_range11[1] = value * y1
            self.y_range11[0] = (value - 1) * y1
            self.graphicsView.setYRange(self.y_range11[0], self.y_range11[1])

            self.timer2.stop()
            y2 = max(data2)
            self.y_range22 = self.graphicsView_2.getViewBox().state["viewRange"][0]
            self.y_range22[1] = value * y2
            self.y_range22[0] = (value - 1) * y2
            self.graphicsView_2.setYRange(self.y_range22[0], self.y_range22[1])

            self.timer3.stop()
            y3 = max(data3)
            self.y_range33 = self.graphicsView_3.getViewBox().state["viewRange"][0]
            self.y_range33[1] = value * y3
            self.y_range33[0] = (value - 1) * y3
            self.graphicsView_3.setYRange(self.y_range33[0], self.y_range33[1])

        elif self.channel2 == True:
            self.timer1.stop()
            y1 = max(data1)
            self.y_range11 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.y_range11[1] = value * y1
            self.y_range11[0] = (value - 1) * y1
            self.graphicsView.setYRange(self.y_range11[0], self.y_range11[1])

            self.timer2.stop()
            y2 = max(data2)
            self.y_range22 = self.graphicsView_2.getViewBox().state["viewRange"][0]
            self.y_range22[1] = value * y2
            self.y_range22[0] = (value - 1) * y2
            self.graphicsView_2.setYRange(self.y_range22[0], self.y_range22[1])

        elif self.channel1 == True:
            self.timer1.stop()
            y1 = max(data1)
            self.y_range11 = self.graphicsView.getViewBox().state["viewRange"][0]
            # pyqtgraph.PlotItem.getViewBox(set)
            self.y_range11[1] = value * y1
            self.y_range11[0] = (value - 1) * y1
            self.graphicsView.setYRange(self.y_range11[0], self.y_range11[1])

    def scroll_horizontal(self):
        value = self.horizontalSlider.value()
        if self.channel3 == True:
            self.timer1.stop()
            self.x_range11 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.x_range11[1] = value * self.curr_x1 / 10
            self.x_range11[0] = (value - 1) * self.curr_x1 / 10
            self.graphicsView.setXRange(self.x_range11[0], self.x_range11[1])

            self.timer2.stop()
            self.x_range22 = self.graphicsView_2.getViewBox().state["viewRange"][0]
            self.x_range22[1] = value * self.curr_x2 / 10
            self.x_range2[0] = (value - 1) * self.curr_x2 / 10
            self.graphicsView_2.setXRange(self.x_range2[0], self.x_range2[1])

            self.timer3.stop()
            self.x_range33 = self.graphicsView_3.getViewBox().state["viewRange"][0]
            self.x_range33[1] = value * self.curr_x3 / 10
            self.x_range33[0] = (value - 1) * self.curr_x3 / 10
            self.graphicsView_3.setXRange(self.x_range33[0], self.x_range33[1])

        elif self.channel2 == True:
            self.timer1.stop()
            self.x_range11 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.x_range11[1] = value * self.curr_x1 / 10
            self.x_range11[0] = (value - 1) * self.curr_x1 / 10
            self.graphicsView.setXRange(self.x_range11[0], self.x_range11[1])

            self.timer2.stop()
            self.x_range22 = self.graphicsView_2.getViewBox().state["viewRange"][0]
            self.x_range22[1] = value * self.curr_x2 / 10
            self.x_range2[0] = (value - 1) * self.curr_x2 / 10
            self.graphicsView_2.setXRange(self.x_range2[0], self.x_range2[1])

        elif self.channel1 == True:
            self.timer1.stop()
            self.x_range11 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.x_range11[1] = value * self.curr_x1 / 10
            self.x_range11[0] = (value - 1) * self.curr_x1 / 10
            self.graphicsView.setXRange(self.x_range11[0], self.x_range11[1])

    def SpeedUp(self):
        self.Interval = int(self.Interval / 2)
        if self.channel3 == True:
            self.timer1.stop()
            self.timer1.start(self.Interval)

            self.timer2.stop()
            self.timer2.start(self.Interval)

            self.timer3.stop()
            self.timer3.start(self.Interval)

        elif self.channel2 == True:
            self.timer1.stop()
            self.timer1.start(self.Interval)

            self.timer2.stop()
            self.timer2.start(self.Interval)

        elif self.channel1 == True:
            self.timer1.stop()
            self.timer1.start(self.Interval)

    def SpeedDown(self):
        self.Interval = int(self.Interval * 2)
        if self.channel3 == True:
            self.timer1.stop()
            self.timer1.start(self.Interval)

            self.timer2.stop()
            self.timer2.start(self.Interval)

            self.timer3.stop()
            self.timer3.start(self.Interval)

        elif self.channel2 == True:
            self.timer1.stop()
            self.timer1.start(self.Interval)

            self.timer2.stop()
            self.timer2.start(self.Interval)

        elif self.channel1 == True:
            self.timer1.stop()
            self.timer1.start(self.Interval)

    def zoom_in(self, val):
        if self.channel3 == True:
            self.x_range1[1] = self.x_range1[1] * val
            self.x_range1[0] = self.x_range1[0] * val
            self.graphicsView.setXRange(self.x_range1[0], self.x_range1[1])

            self.x_range1 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.x_range2[1] = self.x_range2[1] * val
            self.x_range2[0] = self.x_range2[0] * val
            self.graphicsView_2.setXRange(self.x_range2[0], self.x_range2[1])

            self.x_range2 = self.graphicsView_2.getViewBox().state["viewRange"][0]
            self.x_range3[1] = self.x_range3[1] * val
            self.x_range3[0] = self.x_range3[0] * val
            self.graphicsView_3.setXRange(self.x_range3[0], self.x_range3[1])
            self.x_range3 = self.graphicsView_3.getViewBox().state["viewRange"][0]

        elif self.channel2 == True:
            self.x_range1[1] = self.x_range1[1] * val
            self.x_range1[0] = self.x_range1[0] * val
            self.graphicsView.setXRange(self.x_range1[0], self.x_range1[1])
            self.x_range1 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.x_range2[1] = self.x_range2[1] * val
            self.x_range2[0] = self.x_range2[0] * val
            self.graphicsView_2.setXRange(self.x_range2[0], self.x_range2[1])
        elif self.channel1 == True:
            self.x_range1[1] = self.x_range1[1] * val
            self.x_range1[0] = self.x_range1[0] * val
            self.graphicsView.setXRange(self.x_range1[0], self.x_range1[1])
            self.x_range1 = self.graphicsView.getViewBox().state["viewRange"][0]

    def zoom_out(self, val):
        if self.channel3 == True:
            self.x_range1[1] = self.x_range1[1] * val
            self.x_range1[0] = self.x_range1[0] * val
            self.graphicsView.setXRange(self.x_range1[0], self.x_range1[1])
            self.x_range1 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.x_range2[1] = self.x_range2[1] * val
            self.x_range2[0] = self.x_range2[0] * val
            self.graphicsView_2.setXRange(self.x_range2[0], self.x_range2[1])
            self.x_range2 = self.graphicsView_2.getViewBox().state["viewRange"][0]
            self.x_range3[1] = self.x_range3[1] * val
            self.x_range3[0] = self.x_range3[0] * val
            self.graphicsView_3.setXRange(self.x_range3[0], self.x_range3[1])
            self.x_range3 = self.graphicsView_3.getViewBox().state["viewRange"][0]
        elif self.channel2 == True:
            self.x_range1[1] = self.x_range1[1] * val
            self.x_range1[0] = self.x_range1[0] * val
            self.graphicsView.setXRange(self.x_range1[0], self.x_range1[1])
            self.x_range1 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.x_range2[1] = self.x_range2[1] * val
            self.x_range2[0] = self.x_range2[0] * val
            self.graphicsView_2.setXRange(self.x_range2[0], self.x_range2[1])
            self.x_range2 = self.graphicsView_2.getViewBox().state["viewRange"][0]
        elif self.channel1 == True:
            self.x_range1[1] = self.x_range1[1] * val
            self.x_range1[0] = self.x_range1[0] * val
            self.graphicsView.setXRange(self.x_range1[0], self.x_range1[1])
            self.x_range1 = self.graphicsView.getViewBox().state["viewRange"][0]

    def stopGraph(self):
        if self.channel3 == True:
            self.timer1.stop()
            self.timer2.stop()
            self.timer3.stop()
        elif self.channel2 == True:
            self.timer1.stop()
            self.timer2.stop()
        elif self.channel1 == True:
            self.timer1.stop()

    def play(self, Interval):
        if self.channel3 == True:
            self.timer1 = pg.QtCore.QTimer()
            self.timer1.setInterval(50)
            self.timer1.timeout.connect(lambda: self.update(1))
            self.timer1.start(Interval)

            self.timer2 = pg.QtCore.QTimer()
            self.timer2.setInterval(50)
            self.timer2.timeout.connect(lambda: self.update(2))
            self.timer2.start(Interval)

            self.timer3 = pg.QtCore.QTimer()
            self.timer3.setInterval(50)
            self.timer3.timeout.connect(lambda: self.update(3))
            self.timer3.start(Interval)

        elif self.channel2 == True:
            self.timer1 = pg.QtCore.QTimer()
            self.timer1.setInterval(50)
            self.timer1.timeout.connect(lambda: self.update(1))
            self.timer1.start(Interval)
            self.timer2 = pg.QtCore.QTimer()
            self.timer2.setInterval(50)
            self.timer2.timeout.connect(lambda: self.update(2))
            self.timer2.start(Interval)
        elif self.channel1 == True:
            # self.i = 0
            self.timer1 = pg.QtCore.QTimer()
            self.timer1.setInterval(50)
            self.timer1.timeout.connect(lambda: self.update(1))
            self.timer1.start(Interval)

    def update(self, channelNo):
        if channelNo == 1:
            self.x_range1[0] = self.x_range1[0] + 1
            self.x_range1[1] = self.x_range1[1] + 1
            self.graphicsView.plot(time1, data1, pen=self.pen1)
            # self.graphicsView.plotItem.vb.setLimits(xMin=min(time1), xMax=max(time1), yMin=min(data1) - 0.5, yMax=max(data1)+0.5)
            self.graphicsView.setXRange(self.x_range1[0], self.x_range1[1])
            self.curr_x1 = self.x_range1[1]

        elif channelNo == 2:
            self.x_range2[0] = self.x_range2[0] + 1
            self.x_range2[1] = self.x_range2[1] + 1
            self.graphicsView_2.plot(time2, data2, pen=self.pen1)
            self.graphicsView_2.setXRange(self.x_range2[0], self.x_range2[1])
            self.curr_x2 = self.x_range2[1]

        elif channelNo == 3:
            self.x_range3[0] = self.x_range3[0] + 1
            self.x_range3[1] = self.x_range3[1] + 1
            self.graphicsView_3.plot(time3, data3, pen=self.pen1)
            self.graphicsView_3.setXRange(self.x_range3[0], self.x_range3[1])
            self.curr_x3 = self.x_range3[1]

    def Open_file(self):
        global File1, File2, File3, data2, data3, data1, time1, time2, time3, Amplitude_data, time_data, signal_name, sig_data
        options = QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Open csv", QtCore.QDir.rootPath(), "csv(*.csv)"
        )
        data_set = pd.read_csv(fileName, header=None)
        signal_name = fileName[-8:-4]
        data_set1 = data_set[1:].astype(float)

        sig_data.append(data_set1)
        File = data_set.iloc[:, 0]
        Amplitude_data = data_set[1]
        time_data = data_set[0]
        data = []
        time = []

        for i in range(0, (len(Amplitude_data))):
            data.append(Amplitude_data[i])

        for i in range(0, (len(Amplitude_data))):
            time.append(time_data[i])

        if self.channel1 == False:
            self.channel1_path = fileName
            File1 = File
            data1 = data
            time1 = time
            self.graphicsView.setXRange(self.xmin_scale1, self.xmax_scale1)
            self.graphicsView.plotItem.vb.setLimits(
                xMin=min(time1),
                xMax=max(time1),
                yMin=min(data1) - 0.5,
                yMax=max(data1) + 0.5,
            )
            self.x_range1 = self.graphicsView.getViewBox().state["viewRange"][0]
            self.graphicsView.show()
            self.channel1 = True

        elif self.channel2 == False:
            self.channel2_path = fileName
            File2 = File
            data2 = data
            time2 = time
            self.graphicsView_2.setXRange(self.xmin_scale2, self.xmax_scale2)
            self.graphicsView_2.plotItem.vb.setLimits(
                xMin=min(time2),
                xMax=max(time2),
                yMin=min(data2) - 0.5,
                yMax=max(data2) + 0.5,
            )
            self.x_range2 = self.graphicsView_2.getViewBox().state["viewRange"][0]

            self.graphicsView_2.show()
            self.channel2 = True

        elif self.channel3 == False:
            self.channel3_path = fileName
            File3 = File
            data3 = data
            time3 = time
            self.graphicsView_3.setXRange(self.xmin_scale3, self.xmax_scale3)
            self.graphicsView_3.plotItem.vb.setLimits(
                xMin=min(time3),
                xMax=max(time3),
                yMin=min(data3) - 0.5,
                yMax=max(data3) + 0.5,
            )
            self.x_range3 = self.graphicsView_3.getViewBox().state["viewRange"][0]
            self.graphicsView_3.show()
            self.channel3 = True

    def saving_pdf(self, *args, **savefig_kwargs):

        fn, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, "Export PDF", None, "PDF files (.pdf);;All Files()"
        )
        if fn != "":
            if QtCore.QFileInfo(fn).suffix() == "":
                fn += ".pdf"
            table_creation(self, fn)
            print_widget(self.centralwidget, fn)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
