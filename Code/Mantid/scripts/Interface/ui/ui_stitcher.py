# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/stitcher.ui'
#
# Created: Wed Nov 16 13:57:36 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(737, 1163)
        Frame.setFrameShape(QtGui.QFrame.StyledPanel)
        Frame.setFrameShadow(QtGui.QFrame.Raised)
        self.verticalLayout = QtGui.QVBoxLayout(Frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_13 = QtGui.QLabel(Frame)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.verticalLayout.addWidget(self.label_13)
        self.groupBox = QtGui.QGroupBox(Frame)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.low_q_combo = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.low_q_combo.sizePolicy().hasHeightForWidth())
        self.low_q_combo.setSizePolicy(sizePolicy)
        self.low_q_combo.setEditable(True)
        self.low_q_combo.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContentsOnFirstShow)
        self.low_q_combo.setObjectName("low_q_combo")
        self.horizontalLayout_2.addWidget(self.low_q_combo)
        self.low_q_browse_button = QtGui.QPushButton(self.groupBox)
        self.low_q_browse_button.setToolTip("")
        self.low_q_browse_button.setObjectName("low_q_browse_button")
        self.horizontalLayout_2.addWidget(self.low_q_browse_button)
        self.verticalLayout_11.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.low_radio = QtGui.QRadioButton(self.groupBox)
        self.low_radio.setToolTip("")
        self.low_radio.setObjectName("low_radio")
        self.horizontalLayout.addWidget(self.low_radio)
        spacerItem1 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.label_10 = QtGui.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout.addWidget(self.label_10)
        self.low_scale_edit = QtGui.QLineEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.low_scale_edit.sizePolicy().hasHeightForWidth())
        self.low_scale_edit.setSizePolicy(sizePolicy)
        self.low_scale_edit.setStatusTip("")
        self.low_scale_edit.setObjectName("low_scale_edit")
        self.horizontalLayout.addWidget(self.low_scale_edit)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_11.addLayout(self.horizontalLayout)
        self.horizontalLayout_12 = QtGui.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        spacerItem3 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem3)
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_12.addWidget(self.label_8)
        self.low_first_spin = QtGui.QSpinBox(self.groupBox)
        self.low_first_spin.setObjectName("low_first_spin")
        self.horizontalLayout_12.addWidget(self.low_first_spin)
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_12.addWidget(self.label_9)
        self.low_last_spin = QtGui.QSpinBox(self.groupBox)
        self.low_last_spin.setObjectName("low_last_spin")
        self.horizontalLayout_12.addWidget(self.low_last_spin)
        self.label_14 = QtGui.QLabel(self.groupBox)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_12.addWidget(self.label_14)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem4)
        self.verticalLayout_11.addLayout(self.horizontalLayout_12)
        self.verticalLayout.addWidget(self.groupBox)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem5)
        self.horizontalLayout_17 = QtGui.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.line_4 = QtGui.QFrame(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_4.sizePolicy().hasHeightForWidth())
        self.line_4.setSizePolicy(sizePolicy)
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_17.addWidget(self.line_4)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtGui.QLabel(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(50, 0))
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.low_min_edit = QtGui.QLineEdit(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.low_min_edit.sizePolicy().hasHeightForWidth())
        self.low_min_edit.setSizePolicy(sizePolicy)
        self.low_min_edit.setObjectName("low_min_edit")
        self.horizontalLayout_3.addWidget(self.low_min_edit)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtGui.QLabel(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(50, 0))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.low_max_edit = QtGui.QLineEdit(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.low_max_edit.sizePolicy().hasHeightForWidth())
        self.low_max_edit.setSizePolicy(sizePolicy)
        self.low_max_edit.setObjectName("low_max_edit")
        self.horizontalLayout_4.addWidget(self.low_max_edit)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_17.addLayout(self.verticalLayout_3)
        self.low_range_button = QtGui.QPushButton(Frame)
        self.low_range_button.setObjectName("low_range_button")
        self.horizontalLayout_17.addWidget(self.low_range_button)
        self.line_5 = QtGui.QFrame(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_5.sizePolicy().hasHeightForWidth())
        self.line_5.setSizePolicy(sizePolicy)
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.horizontalLayout_17.addWidget(self.line_5)
        self.verticalLayout.addLayout(self.horizontalLayout_17)
        spacerItem6 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem6)
        self.groupBox_2 = QtGui.QGroupBox(Frame)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.medium_q_combo = QtGui.QComboBox(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.medium_q_combo.sizePolicy().hasHeightForWidth())
        self.medium_q_combo.setSizePolicy(sizePolicy)
        self.medium_q_combo.setEditable(True)
        self.medium_q_combo.setObjectName("medium_q_combo")
        self.horizontalLayout_5.addWidget(self.medium_q_combo)
        self.medium_q_browse_button = QtGui.QPushButton(self.groupBox_2)
        self.medium_q_browse_button.setToolTip("")
        self.medium_q_browse_button.setObjectName("medium_q_browse_button")
        self.horizontalLayout_5.addWidget(self.medium_q_browse_button)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem7 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem7)
        self.medium_radio = QtGui.QRadioButton(self.groupBox_2)
        self.medium_radio.setObjectName("medium_radio")
        self.horizontalLayout_6.addWidget(self.medium_radio)
        spacerItem8 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem8)
        self.label_11 = QtGui.QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_6.addWidget(self.label_11)
        self.medium_scale_edit = QtGui.QLineEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.medium_scale_edit.sizePolicy().hasHeightForWidth())
        self.medium_scale_edit.setSizePolicy(sizePolicy)
        self.medium_scale_edit.setStatusTip("")
        self.medium_scale_edit.setObjectName("medium_scale_edit")
        self.horizontalLayout_6.addWidget(self.medium_scale_edit)
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem9)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        spacerItem10 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem10)
        self.label_15 = QtGui.QLabel(self.groupBox_2)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_13.addWidget(self.label_15)
        self.medium_first_spin = QtGui.QSpinBox(self.groupBox_2)
        self.medium_first_spin.setObjectName("medium_first_spin")
        self.horizontalLayout_13.addWidget(self.medium_first_spin)
        self.label_16 = QtGui.QLabel(self.groupBox_2)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_13.addWidget(self.label_16)
        self.medium_last_spin = QtGui.QSpinBox(self.groupBox_2)
        self.medium_last_spin.setObjectName("medium_last_spin")
        self.horizontalLayout_13.addWidget(self.medium_last_spin)
        self.label_17 = QtGui.QLabel(self.groupBox_2)
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_13.addWidget(self.label_17)
        spacerItem11 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem11)
        self.verticalLayout_5.addLayout(self.horizontalLayout_13)
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem12 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem12)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.line_2 = QtGui.QFrame(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_11.addWidget(self.line_2)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_5 = QtGui.QLabel(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QtCore.QSize(50, 0))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_7.addWidget(self.label_5)
        self.medium_min_edit = QtGui.QLineEdit(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.medium_min_edit.sizePolicy().hasHeightForWidth())
        self.medium_min_edit.setSizePolicy(sizePolicy)
        self.medium_min_edit.setObjectName("medium_min_edit")
        self.horizontalLayout_7.addWidget(self.medium_min_edit)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_6 = QtGui.QLabel(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QtCore.QSize(50, 0))
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_8.addWidget(self.label_6)
        self.medium_max_edit = QtGui.QLineEdit(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.medium_max_edit.sizePolicy().hasHeightForWidth())
        self.medium_max_edit.setSizePolicy(sizePolicy)
        self.medium_max_edit.setObjectName("medium_max_edit")
        self.horizontalLayout_8.addWidget(self.medium_max_edit)
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_11.addLayout(self.verticalLayout_4)
        self.medium_range_button = QtGui.QPushButton(Frame)
        self.medium_range_button.setObjectName("medium_range_button")
        self.horizontalLayout_11.addWidget(self.medium_range_button)
        self.line_3 = QtGui.QFrame(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_3.sizePolicy().hasHeightForWidth())
        self.line_3.setSizePolicy(sizePolicy)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_11.addWidget(self.line_3)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        spacerItem13 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem13)
        self.groupBox_3 = QtGui.QGroupBox(Frame)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_7 = QtGui.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_9.addWidget(self.label_7)
        self.high_q_combo = QtGui.QComboBox(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.high_q_combo.sizePolicy().hasHeightForWidth())
        self.high_q_combo.setSizePolicy(sizePolicy)
        self.high_q_combo.setEditable(True)
        self.high_q_combo.setObjectName("high_q_combo")
        self.horizontalLayout_9.addWidget(self.high_q_combo)
        self.high_q_browse_button = QtGui.QPushButton(self.groupBox_3)
        self.high_q_browse_button.setToolTip("")
        self.high_q_browse_button.setObjectName("high_q_browse_button")
        self.horizontalLayout_9.addWidget(self.high_q_browse_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtGui.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem14 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem14)
        self.high_radio = QtGui.QRadioButton(self.groupBox_3)
        self.high_radio.setObjectName("high_radio")
        self.horizontalLayout_10.addWidget(self.high_radio)
        spacerItem15 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem15)
        self.label_12 = QtGui.QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_10.addWidget(self.label_12)
        self.high_scale_edit = QtGui.QLineEdit(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.high_scale_edit.sizePolicy().hasHeightForWidth())
        self.high_scale_edit.setSizePolicy(sizePolicy)
        self.high_scale_edit.setStatusTip("")
        self.high_scale_edit.setObjectName("high_scale_edit")
        self.horizontalLayout_10.addWidget(self.high_scale_edit)
        spacerItem16 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem16)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_14 = QtGui.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        spacerItem17 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem17)
        self.label_18 = QtGui.QLabel(self.groupBox_3)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_14.addWidget(self.label_18)
        self.high_first_spin = QtGui.QSpinBox(self.groupBox_3)
        self.high_first_spin.setObjectName("high_first_spin")
        self.horizontalLayout_14.addWidget(self.high_first_spin)
        self.label_19 = QtGui.QLabel(self.groupBox_3)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_14.addWidget(self.label_19)
        self.high_last_spin = QtGui.QSpinBox(self.groupBox_3)
        self.high_last_spin.setObjectName("high_last_spin")
        self.horizontalLayout_14.addWidget(self.high_last_spin)
        self.label_20 = QtGui.QLabel(self.groupBox_3)
        self.label_20.setObjectName("label_20")
        self.horizontalLayout_14.addWidget(self.label_20)
        spacerItem18 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem18)
        self.verticalLayout_2.addLayout(self.horizontalLayout_14)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.line = QtGui.QFrame(Frame)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_16 = QtGui.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        spacerItem19 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_16.addItem(spacerItem19)
        self.apply_button = QtGui.QPushButton(Frame)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(223, 242, 208))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(223, 242, 208))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(223, 242, 208))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.apply_button.setPalette(palette)
        self.apply_button.setAutoFillBackground(False)
        self.apply_button.setObjectName("apply_button")
        self.horizontalLayout_16.addWidget(self.apply_button)
        self.save_result_button = QtGui.QPushButton(Frame)
        self.save_result_button.setObjectName("save_result_button")
        self.horizontalLayout_16.addWidget(self.save_result_button)
        self.verticalLayout.addLayout(self.horizontalLayout_16)
        spacerItem20 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem20)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QtGui.QApplication.translate("Frame", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("Frame", "Select the I(Q) data sets you want to combine.", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Frame", "Low Q", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Frame", "I(q) file:", None, QtGui.QApplication.UnicodeUTF8))
        self.low_q_combo.setToolTip(QtGui.QApplication.translate("Frame", "Select a reduced data file or a reduced workspace.", None, QtGui.QApplication.UnicodeUTF8))
        self.low_q_browse_button.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.low_radio.setText(QtGui.QApplication.translate("Frame", "Normalize to this data set", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Frame", "Scaling factor", None, QtGui.QApplication.UnicodeUTF8))
        self.low_scale_edit.setToolTip(QtGui.QApplication.translate("Frame", "Enter a scaling factor and hit enter to apply.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Frame", "Skip first ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Frame", "and last", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("Frame", "points", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Frame", "Min Q", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Frame", "Max Q", None, QtGui.QApplication.UnicodeUTF8))
        self.low_range_button.setToolTip(QtGui.QApplication.translate("Frame", "Click to select the Q region used to scale the low-Q and medium-Q data sets.", None, QtGui.QApplication.UnicodeUTF8))
        self.low_range_button.setText(QtGui.QApplication.translate("Frame", "Pick Overlap Region", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Frame", "Medium Q", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Frame", "I(q) file:", None, QtGui.QApplication.UnicodeUTF8))
        self.medium_q_combo.setToolTip(QtGui.QApplication.translate("Frame", "Select a reduced data file or a reduced workspace.", None, QtGui.QApplication.UnicodeUTF8))
        self.medium_q_browse_button.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.medium_radio.setText(QtGui.QApplication.translate("Frame", "Normalize to this data set", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Frame", "Scaling factor", None, QtGui.QApplication.UnicodeUTF8))
        self.medium_scale_edit.setToolTip(QtGui.QApplication.translate("Frame", "Enter a scaling factor and hit enter to apply.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("Frame", "Skip first ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setText(QtGui.QApplication.translate("Frame", "and last", None, QtGui.QApplication.UnicodeUTF8))
        self.label_17.setText(QtGui.QApplication.translate("Frame", "points", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Frame", "Min Q", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Frame", "Max Q", None, QtGui.QApplication.UnicodeUTF8))
        self.medium_range_button.setToolTip(QtGui.QApplication.translate("Frame", "Click to select the Q region used to scale the low-Q and medium-Q data sets.", None, QtGui.QApplication.UnicodeUTF8))
        self.medium_range_button.setText(QtGui.QApplication.translate("Frame", "Pick Overlap Region", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Frame", "High Q", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Frame", "I(q) file:", None, QtGui.QApplication.UnicodeUTF8))
        self.high_q_combo.setToolTip(QtGui.QApplication.translate("Frame", "Select a reduced data file or a reduced workspace.", None, QtGui.QApplication.UnicodeUTF8))
        self.high_q_browse_button.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.high_radio.setText(QtGui.QApplication.translate("Frame", "Normalize to this data set", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("Frame", "Scaling factor", None, QtGui.QApplication.UnicodeUTF8))
        self.high_scale_edit.setToolTip(QtGui.QApplication.translate("Frame", "Enter a scaling factor and hit enter to apply.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_18.setText(QtGui.QApplication.translate("Frame", "Skip first ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_19.setText(QtGui.QApplication.translate("Frame", "and last", None, QtGui.QApplication.UnicodeUTF8))
        self.label_20.setText(QtGui.QApplication.translate("Frame", "points", None, QtGui.QApplication.UnicodeUTF8))
        self.apply_button.setToolTip(QtGui.QApplication.translate("Frame", "Click to automatically scale all data sets to the selected reference.", None, QtGui.QApplication.UnicodeUTF8))
        self.apply_button.setText(QtGui.QApplication.translate("Frame", "Auto Scale", None, QtGui.QApplication.UnicodeUTF8))
        self.save_result_button.setText(QtGui.QApplication.translate("Frame", "Save Result", None, QtGui.QApplication.UnicodeUTF8))

