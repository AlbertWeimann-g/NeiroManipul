
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from motion.core import RobotControl 
import os

class Ui_MainWindow(QtWidgets.QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1143, 1078)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        self.pushButtonKoorpr = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonKoorpr.setGeometry(QtCore.QRect(470, 700, 88, 27))
        self.pushButtonKoorpr.setText("Применить")
        self.pushButtonKoorpr.clicked.connect(self.auto_move)

        self.textEditLog = QtWidgets.QTextEdit(self.centralwidget)
        self.textEditLog.setGeometry(QtCore.QRect(30, 800, 651, 191))

        self.pushButtonStopped = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStopped.setGeometry(QtCore.QRect(470, 200, 71, 31))
        self.pushButtonStopped.setText("Stopped")

        self.pushButtonWork = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonWork.setGeometry(QtCore.QRect(550, 200, 71, 31))
        self.pushButtonWork.setText("Work")

        self.pushButtonOFf = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonOFf.setGeometry(QtCore.QRect(630, 200, 71, 31))
        self.pushButtonOFf.setText("Off")

        self.pushButtonWait = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonWait.setGeometry(QtCore.QRect(710, 200, 71, 31))
        self.pushButtonWait.setText("Wait")

        self.tableWidgeKoor = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgeKoor.setGeometry(QtCore.QRect(10, 670, 441, 61))
        self.tableWidgeKoor.setColumnCount(4)
        self.tableWidgeKoor.setRowCount(1)
        for i, label in enumerate(["x", "y", "z", "gripper"]):
            self.tableWidgeKoor.setHorizontalHeaderItem(i, QTableWidgetItem(label))

        self.tableWidgetActualPose = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgetActualPose.setGeometry(QtCore.QRect(120, 70, 451, 71))
        self.tableWidgetActualPose.setColumnCount(4)
        self.tableWidgetActualPose.setRowCount(1)
        for i, label in enumerate(["x", "y", "z", "gripper"]):
            self.tableWidgetActualPose.setHorizontalHeaderItem(i, QTableWidgetItem(label))

        self.tableWidgetSOST = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgetSOST.setGeometry(QtCore.QRect(10, 440, 681, 161))
        self.tableWidgetSOST.setColumnCount(6)
        self.tableWidgetSOST.setRowCount(4)

        self.robot = RobotControl()
        self.robot.connect()
        self.robot.engage()

    def auto_move(self):
        try:
            x = float(self.tableWidgeKoor.item(0, 0).text())
            y = float(self.tableWidgeKoor.item(0, 1).text())
            z = float(self.tableWidgeKoor.item(0, 2).text())
            gripper = self.tableWidgeKoor.item(0, 3).text().lower() == "true"

            if not (0 <= x <= 950 and 0 <= y <= 950 and 0 <= z <= 950):
                self.log("Ошибка: координаты вне рабочей зоны")
                return

            self.set_status("Work")
            self.robot.moveL([x, y, z])
            if gripper:
                self.robot.controlGripper(True)
            self.robot.moveL([x+50, y+50, z]) 
            if gripper:
                self.robot.controlGripper(False)

            self.update_pose_table([x+50, y+50, z, "Open" if not gripper else "Closed"])
            self.update_motor_table()
            self.log(f"Перемещение в ({x}, {y}, {z}) завершено.")

        except Exception as e:
            self.log(f"Ошибка: {e}")
            self.set_status("Stopped")

    def update_pose_table(self, coords):
        for i, val in enumerate(coords):
            self.tableWidgetActualPose.setItem(0, i, QTableWidgetItem(str(val)))

    def update_motor_table(self):
        states = self.robot.getMotorStates()  
        for row in range(min(4, len(states))):
            for col in range(min(6, len(states[row]))):
                self.tableWidgetSOST.setItem(row, col, QTableWidgetItem(str(states[row][col])))

    def log(self, text):
        self.textEditLog.append(text)
        with open("log.txt", "a") as f:
            f.write(text + "\n")

    def set_status(self, status):
        colors = {"Stopped": "gray", "Work": "green", "Off": "red", "Wait": "yellow"}
        for s in colors:
            getattr(self, f"pushButton{s}").setStyleSheet(f"background-color: none")
        getattr(self, f"pushButton{status}").setStyleSheet(f"background-color: {colors[status]}")
