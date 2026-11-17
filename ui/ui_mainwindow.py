# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QMenuBar, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QSpinBox, QStatusBar, QToolButton,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 820)
        MainWindow.setStyleSheet(u"\n"
"QMainWindow, QWidget#centralwidget { background-color:#0E0F11; }\n"
"QLabel { color:#D8DCE0; font-size:12px; }\n"
"QLabel#titleLabel { color:#7CFC9A; font-size:20px; font-weight:bold; letter-spacing:1px; }\n"
"QLabel#subtitleLabel { color:#8A9099; font-size:12px; }\n"
"QFrame#header { background-color:#16181B; border:1px solid #242830; border-radius:6px; }\n"
"QGroupBox { background-color:#16181B; border:1px solid #242830; border-radius:8px; margin-top:14px; padding:12px 8px 8px 8px; font-weight:bold; color:#7CFC9A; }\n"
"QGroupBox::title { subcontrol-origin:margin; left:12px; padding:0 6px; color:#7CFC9A; }\n"
"QDoubleSpinBox, QSpinBox { background-color:#0E0F11; color:#E6E9EC; border:1px solid #2E333B; border-radius:4px; padding:3px 6px; min-height:22px; }\n"
"QDoubleSpinBox:focus, QSpinBox:focus { border-color:#7CFC9A; }\n"
"QRadioButton, QCheckBox { color:#E6E9EC; font-size:12px; spacing:8px; }\n"
"QRadioButton:checked { color:#7CFC9A; }\n"
"QRadioButton::indicator { width:14px; height:14px; border-ra"
                        "dius:8px; border:2px solid #6A707A; background-color:#2A2D33; }\n"
"QRadioButton::indicator:hover { border-color:#7CFC9A; }\n"
"QRadioButton::indicator:checked { border:2px solid #7CFC9A; background-color:qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #7CFC9A, stop:0.5 #7CFC9A, stop:0.6 #2A2D33, stop:1 #2A2D33); }\n"
"QToolButton { background-color:#2A2D33; color:#E6E9EC; border:1px solid #3A3F47; border-radius:6px; font-size:18px; }\n"
"QToolButton:hover { border-color:#7CFC9A; }\n"
"QToolButton:pressed { background-color:#7CFC9A; color:#0E0F11; }\n"
"QToolButton:disabled { color:#5A5F66; }\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.rootLayout = QVBoxLayout(self.centralwidget)
        self.rootLayout.setSpacing(10)
        self.rootLayout.setObjectName(u"rootLayout")
        self.rootLayout.setContentsMargins(12, 12, 12, 12)
        self.header = QFrame(self.centralwidget)
        self.header.setObjectName(u"header")
        self.header.setMinimumSize(QSize(0, 48))
        self.headerLayout = QHBoxLayout(self.header)
        self.headerLayout.setObjectName(u"headerLayout")
        self.titleLabel = QLabel(self.header)
        self.titleLabel.setObjectName(u"titleLabel")

        self.headerLayout.addWidget(self.titleLabel)

        self.subtitleLabel = QLabel(self.header)
        self.subtitleLabel.setObjectName(u"subtitleLabel")

        self.headerLayout.addWidget(self.subtitleLabel)

        self.headerSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.headerSpacer)


        self.rootLayout.addWidget(self.header)

        self.middleLayout = QHBoxLayout()
        self.middleLayout.setSpacing(10)
        self.middleLayout.setObjectName(u"middleLayout")
        self.lidarView = LidarView(self.centralwidget)
        self.lidarView.setObjectName(u"lidarView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lidarView.sizePolicy().hasHeightForWidth())
        self.lidarView.setSizePolicy(sizePolicy)

        self.middleLayout.addWidget(self.lidarView)

        self.gaugeColumn = QVBoxLayout()
        self.gaugeColumn.setSpacing(10)
        self.gaugeColumn.setObjectName(u"gaugeColumn")
        self.gauge1Box = QGroupBox(self.centralwidget)
        self.gauge1Box.setObjectName(u"gauge1Box")
        self.panLayout = QVBoxLayout(self.gauge1Box)
        self.panLayout.setObjectName(u"panLayout")
        self.gauge1 = GaugePanel(self.gauge1Box)
        self.gauge1.setObjectName(u"gauge1")
        self.gauge1.setMinimum(-180.000000000000000)
        self.gauge1.setMaximum(180.000000000000000)

        self.panLayout.addWidget(self.gauge1)


        self.gaugeColumn.addWidget(self.gauge1Box)

        self.gauge2Box = QGroupBox(self.centralwidget)
        self.gauge2Box.setObjectName(u"gauge2Box")
        self.tiltLayout = QVBoxLayout(self.gauge2Box)
        self.tiltLayout.setObjectName(u"tiltLayout")
        self.gauge2 = GaugePanel(self.gauge2Box)
        self.gauge2.setObjectName(u"gauge2")
        self.gauge2.setMinimum(-90.000000000000000)
        self.gauge2.setMaximum(90.000000000000000)

        self.tiltLayout.addWidget(self.gauge2)


        self.gaugeColumn.addWidget(self.gauge2Box)


        self.middleLayout.addLayout(self.gaugeColumn)


        self.rootLayout.addLayout(self.middleLayout)

        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.setSpacing(10)
        self.bottomLayout.setObjectName(u"bottomLayout")
        self.modeBox = QGroupBox(self.centralwidget)
        self.modeBox.setObjectName(u"modeBox")
        self.modeGrid = QGridLayout(self.modeBox)
        self.modeGrid.setObjectName(u"modeGrid")
        self.swSearchLabel = QLabel(self.modeBox)
        self.swSearchLabel.setObjectName(u"swSearchLabel")

        self.modeGrid.addWidget(self.swSearchLabel, 0, 0, 1, 1)

        self.swSearch = ToggleSwitch(self.modeBox)
        self.swSearch.setObjectName(u"swSearch")

        self.modeGrid.addWidget(self.swSearch, 0, 1, 1, 1)

        self.swStaticLabel = QLabel(self.modeBox)
        self.swStaticLabel.setObjectName(u"swStaticLabel")

        self.modeGrid.addWidget(self.swStaticLabel, 1, 0, 1, 1)

        self.swStatic = ToggleSwitch(self.modeBox)
        self.swStatic.setObjectName(u"swStatic")

        self.modeGrid.addWidget(self.swStatic, 1, 1, 1, 1)

        self.swFireLabel = QLabel(self.modeBox)
        self.swFireLabel.setObjectName(u"swFireLabel")

        self.modeGrid.addWidget(self.swFireLabel, 2, 0, 1, 1)

        self.swFire = ToggleSwitch(self.modeBox)
        self.swFire.setObjectName(u"swFire")

        self.modeGrid.addWidget(self.swFire, 2, 1, 1, 1)

        self.rangeLabel = QLabel(self.modeBox)
        self.rangeLabel.setObjectName(u"rangeLabel")

        self.modeGrid.addWidget(self.rangeLabel, 3, 0, 1, 1)

        self.rangeSpin = QSpinBox(self.modeBox)
        self.rangeSpin.setObjectName(u"rangeSpin")
        self.rangeSpin.setMinimum(10)
        self.rangeSpin.setMaximum(500)
        self.rangeSpin.setValue(100)

        self.modeGrid.addWidget(self.rangeSpin, 3, 1, 1, 1)


        self.bottomLayout.addWidget(self.modeBox)

        self.pidBox = QGroupBox(self.centralwidget)
        self.pidBox.setObjectName(u"pidBox")
        self.pidGrid = QGridLayout(self.pidBox)
        self.pidGrid.setObjectName(u"pidGrid")
        self.pidPanLabel = QLabel(self.pidBox)
        self.pidPanLabel.setObjectName(u"pidPanLabel")

        self.pidGrid.addWidget(self.pidPanLabel, 0, 1, 1, 1)

        self.pidTiltLabel = QLabel(self.pidBox)
        self.pidTiltLabel.setObjectName(u"pidTiltLabel")

        self.pidGrid.addWidget(self.pidTiltLabel, 0, 2, 1, 1)

        self.pidKpLabel = QLabel(self.pidBox)
        self.pidKpLabel.setObjectName(u"pidKpLabel")

        self.pidGrid.addWidget(self.pidKpLabel, 1, 0, 1, 1)

        self.kpPan = QDoubleSpinBox(self.pidBox)
        self.kpPan.setObjectName(u"kpPan")
        self.kpPan.setDecimals(4)
        self.kpPan.setMinimum(0.000000000000000)
        self.kpPan.setMaximum(10000.000000000000000)
        self.kpPan.setSingleStep(0.100000000000000)
        self.kpPan.setValue(1.000000000000000)

        self.pidGrid.addWidget(self.kpPan, 1, 1, 1, 1)

        self.kpTilt = QDoubleSpinBox(self.pidBox)
        self.kpTilt.setObjectName(u"kpTilt")
        self.kpTilt.setDecimals(4)
        self.kpTilt.setMinimum(0.000000000000000)
        self.kpTilt.setMaximum(10000.000000000000000)
        self.kpTilt.setSingleStep(0.100000000000000)
        self.kpTilt.setValue(1.000000000000000)

        self.pidGrid.addWidget(self.kpTilt, 1, 2, 1, 1)

        self.pidKiLabel = QLabel(self.pidBox)
        self.pidKiLabel.setObjectName(u"pidKiLabel")

        self.pidGrid.addWidget(self.pidKiLabel, 2, 0, 1, 1)

        self.kiPan = QDoubleSpinBox(self.pidBox)
        self.kiPan.setObjectName(u"kiPan")
        self.kiPan.setDecimals(4)
        self.kiPan.setMinimum(0.000000000000000)
        self.kiPan.setMaximum(10000.000000000000000)
        self.kiPan.setSingleStep(0.010000000000000)
        self.kiPan.setValue(0.000000000000000)

        self.pidGrid.addWidget(self.kiPan, 2, 1, 1, 1)

        self.kiTilt = QDoubleSpinBox(self.pidBox)
        self.kiTilt.setObjectName(u"kiTilt")
        self.kiTilt.setDecimals(4)
        self.kiTilt.setMinimum(0.000000000000000)
        self.kiTilt.setMaximum(10000.000000000000000)
        self.kiTilt.setSingleStep(0.010000000000000)
        self.kiTilt.setValue(0.000000000000000)

        self.pidGrid.addWidget(self.kiTilt, 2, 2, 1, 1)

        self.pidKdLabel = QLabel(self.pidBox)
        self.pidKdLabel.setObjectName(u"pidKdLabel")

        self.pidGrid.addWidget(self.pidKdLabel, 3, 0, 1, 1)

        self.kdPan = QDoubleSpinBox(self.pidBox)
        self.kdPan.setObjectName(u"kdPan")
        self.kdPan.setDecimals(4)
        self.kdPan.setMinimum(0.000000000000000)
        self.kdPan.setMaximum(10000.000000000000000)
        self.kdPan.setSingleStep(0.010000000000000)
        self.kdPan.setValue(0.000000000000000)

        self.pidGrid.addWidget(self.kdPan, 3, 1, 1, 1)

        self.kdTilt = QDoubleSpinBox(self.pidBox)
        self.kdTilt.setObjectName(u"kdTilt")
        self.kdTilt.setDecimals(4)
        self.kdTilt.setMinimum(0.000000000000000)
        self.kdTilt.setMaximum(10000.000000000000000)
        self.kdTilt.setSingleStep(0.010000000000000)
        self.kdTilt.setValue(0.000000000000000)

        self.pidGrid.addWidget(self.kdTilt, 3, 2, 1, 1)


        self.bottomLayout.addWidget(self.pidBox)

        self.fireCtrlBox = QGroupBox(self.centralwidget)
        self.fireCtrlBox.setObjectName(u"fireCtrlBox")
        self.fireCtrlLayout = QVBoxLayout(self.fireCtrlBox)
        self.fireCtrlLayout.setObjectName(u"fireCtrlLayout")
        self.pushButton = QPushButton(self.fireCtrlBox)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(110, 110))
        self.pushButton.setMaximumSize(QSize(110, 110))
        self.pushButton.setStyleSheet(u"QPushButton { background-color:#2A2D33; color:#E6E9EC; border:3px solid #FF3B30; border-radius:55px; font-size:15px; font-weight:bold; }\n"
"QPushButton:disabled { border-color:#4A4D53; color:#6A6D73; }\n"
"QPushButton:pressed { background-color:#FF3B30; color:white; }")

        self.fireCtrlLayout.addWidget(self.pushButton, 0, Qt.AlignCenter)


        self.bottomLayout.addWidget(self.fireCtrlBox)

        self.motionCtrlBox = QGroupBox(self.centralwidget)
        self.motionCtrlBox.setObjectName(u"motionCtrlBox")
        self.motionLayout = QHBoxLayout(self.motionCtrlBox)
        self.motionLayout.setObjectName(u"motionLayout")
        self.padGrid = QGridLayout()
        self.padGrid.setObjectName(u"padGrid")
        self.padUp = QToolButton(self.motionCtrlBox)
        self.padUp.setObjectName(u"padUp")
        self.padUp.setMinimumSize(QSize(60, 44))
        self.padUp.setMaximumSize(QSize(60, 44))
        self.padUp.setAutoRepeat(True)
        self.padUp.setAutoRepeatInterval(80)

        self.padGrid.addWidget(self.padUp, 0, 1, 1, 1)

        self.padLeft = QToolButton(self.motionCtrlBox)
        self.padLeft.setObjectName(u"padLeft")
        self.padLeft.setStyleSheet(u"font-size:30px;")
        self.padLeft.setMinimumSize(QSize(60, 44))
        self.padLeft.setMaximumSize(QSize(60, 44))
        self.padLeft.setAutoRepeat(True)
        self.padLeft.setAutoRepeatInterval(80)

        self.padGrid.addWidget(self.padLeft, 1, 0, 1, 1)

        self.padCenter = QToolButton(self.motionCtrlBox)
        self.padCenter.setObjectName(u"padCenter")
        self.padCenter.setMinimumSize(QSize(60, 44))
        self.padCenter.setMaximumSize(QSize(60, 44))
        self.padCenter.setAutoRepeat(True)
        self.padCenter.setAutoRepeatInterval(80)

        self.padGrid.addWidget(self.padCenter, 1, 1, 1, 1)

        self.padRight = QToolButton(self.motionCtrlBox)
        self.padRight.setObjectName(u"padRight")
        self.padRight.setStyleSheet(u"font-size:30px;")
        self.padRight.setMinimumSize(QSize(60, 44))
        self.padRight.setMaximumSize(QSize(60, 44))
        self.padRight.setAutoRepeat(True)
        self.padRight.setAutoRepeatInterval(80)

        self.padGrid.addWidget(self.padRight, 1, 2, 1, 1)

        self.padDown = QToolButton(self.motionCtrlBox)
        self.padDown.setObjectName(u"padDown")
        self.padDown.setMinimumSize(QSize(60, 44))
        self.padDown.setMaximumSize(QSize(60, 44))
        self.padDown.setAutoRepeat(True)
        self.padDown.setAutoRepeatInterval(80)

        self.padGrid.addWidget(self.padDown, 2, 1, 1, 1)


        self.motionLayout.addLayout(self.padGrid)

        self.stepLayout = QVBoxLayout()
        self.stepLayout.setObjectName(u"stepLayout")
        self.step01 = QRadioButton(self.motionCtrlBox)
        self.step01.setObjectName(u"step01")

        self.stepLayout.addWidget(self.step01)

        self.step05 = QRadioButton(self.motionCtrlBox)
        self.step05.setObjectName(u"step05")

        self.stepLayout.addWidget(self.step05)

        self.step1 = QRadioButton(self.motionCtrlBox)
        self.step1.setObjectName(u"step1")

        self.stepLayout.addWidget(self.step1)

        self.step10 = QRadioButton(self.motionCtrlBox)
        self.step10.setObjectName(u"step10")

        self.stepLayout.addWidget(self.step10)

        self.step100 = QRadioButton(self.motionCtrlBox)
        self.step100.setObjectName(u"step100")
        self.step100.setChecked(True)

        self.stepLayout.addWidget(self.step100)


        self.motionLayout.addLayout(self.stepLayout)


        self.bottomLayout.addWidget(self.motionCtrlBox)

        self.launcherModeBox = QGroupBox(self.centralwidget)
        self.launcherModeBox.setObjectName(u"launcherModeBox")
        self.launcherModeGrid = QGridLayout(self.launcherModeBox)
        self.launcherModeGrid.setObjectName(u"launcherModeGrid")
        self.btnServoOn = QPushButton(self.launcherModeBox)
        self.btnServoOn.setObjectName(u"btnServoOn")
        self.btnServoOn.setMinimumSize(QSize(110, 40))

        self.launcherModeGrid.addWidget(self.btnServoOn, 0, 0, 1, 1)

        self.btnServoOff = QPushButton(self.launcherModeBox)
        self.btnServoOff.setObjectName(u"btnServoOff")
        self.btnServoOff.setMinimumSize(QSize(110, 40))

        self.launcherModeGrid.addWidget(self.btnServoOff, 0, 1, 1, 1)

        self.btnHome = QPushButton(self.launcherModeBox)
        self.btnHome.setObjectName(u"btnHome")
        self.btnHome.setMinimumSize(QSize(110, 40))

        self.launcherModeGrid.addWidget(self.btnHome, 1, 0, 1, 1)

        self.btnAuto = QPushButton(self.launcherModeBox)
        self.btnAuto.setObjectName(u"btnAuto")
        self.btnAuto.setMinimumSize(QSize(110, 40))

        self.launcherModeGrid.addWidget(self.btnAuto, 1, 1, 1, 1)


        self.bottomLayout.addWidget(self.launcherModeBox)


        self.rootLayout.addLayout(self.bottomLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LIDAR TRACKER | PAN-TILT CONTROL", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"LIDAR TRACKER", None))
        self.subtitleLabel.setText(QCoreApplication.translate("MainWindow", u"|  PAN-TILT CONTROL", None))
        self.gauge1Box.setTitle(QCoreApplication.translate("MainWindow", u"PAN ANGLE", None))
        self.gauge1.setTitle(QCoreApplication.translate("MainWindow", u"PAN", None))
        self.gauge2Box.setTitle(QCoreApplication.translate("MainWindow", u"TILT ANGLE", None))
        self.gauge2.setTitle(QCoreApplication.translate("MainWindow", u"TILT", None))
        self.modeBox.setTitle(QCoreApplication.translate("MainWindow", u"MODE", None))
        self.swSearchLabel.setText(QCoreApplication.translate("MainWindow", u"Search (probe off)", None))
        self.swStaticLabel.setText(QCoreApplication.translate("MainWindow", u"Hide Static", None))
        self.swFireLabel.setText(QCoreApplication.translate("MainWindow", u"Fire enable", None))
        self.rangeLabel.setText(QCoreApplication.translate("MainWindow", u"Range", None))
        self.rangeSpin.setSuffix(QCoreApplication.translate("MainWindow", u" m", None))
        self.pidBox.setTitle(QCoreApplication.translate("MainWindow", u"PID", None))
        self.pidPanLabel.setText(QCoreApplication.translate("MainWindow", u"Pan", None))
        self.pidTiltLabel.setText(QCoreApplication.translate("MainWindow", u"Tilt", None))
        self.pidKpLabel.setText(QCoreApplication.translate("MainWindow", u"Kp", None))
        self.pidKiLabel.setText(QCoreApplication.translate("MainWindow", u"Ki", None))
        self.pidKdLabel.setText(QCoreApplication.translate("MainWindow", u"Kd", None))
        self.fireCtrlBox.setTitle(QCoreApplication.translate("MainWindow", u"fire controller", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"FIRE", None))
        self.motionCtrlBox.setTitle(QCoreApplication.translate("MainWindow", u"motion controller", None))
        self.padUp.setText(QCoreApplication.translate("MainWindow", u"\u25b2", None))
        self.padLeft.setText(QCoreApplication.translate("MainWindow", u"\u25c0", None))
        self.padCenter.setText(QCoreApplication.translate("MainWindow", u"\u25cf", None))
        self.padRight.setText(QCoreApplication.translate("MainWindow", u"\u25b6", None))
        self.padDown.setText(QCoreApplication.translate("MainWindow", u"\u25bc", None))
        self.step01.setText(QCoreApplication.translate("MainWindow", u"0.1 mm", None))
        self.step05.setText(QCoreApplication.translate("MainWindow", u"0.5 mm", None))
        self.step1.setText(QCoreApplication.translate("MainWindow", u"1 mm", None))
        self.step10.setText(QCoreApplication.translate("MainWindow", u"10 mm", None))
        self.step100.setText(QCoreApplication.translate("MainWindow", u"100 mm", None))
        self.launcherModeBox.setTitle(QCoreApplication.translate("MainWindow", u"Luncher mode", None))
        self.btnServoOn.setText(QCoreApplication.translate("MainWindow", u"Servo on", None))
        self.btnServoOff.setText(QCoreApplication.translate("MainWindow", u"Servo Off", None))
        self.btnHome.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.btnAuto.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
    # retranslateUi

