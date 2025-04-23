# -*- coding: utf-8 -*-
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from motion.core import RobotControl
import threading
import time

class Ui_MainWindow(QtWidgets.QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        self.textEditLog = QtWidgets.QTextEdit(self.centralwidget)
        self.textEditLog.setGeometry(QtCore.QRect(20, 700, 600, 200))

        # Цветовые индикаторы
        self.pushButtonRed = self.createButton("Красный", 650, 700)
        self.pushButtonYellow = self.createButton("Жёлтый", 650, 740)
        self.pushButtonGreen = self.createButton("Зелёный", 650, 780)
        self.pushButtonBlue = self.createButton("Синий", 650, 820)

        # Фигурные индикаторы
        self.pushButtonSquare = self.createButton("Квадрат", 770, 700)
        self.pushButtonTriangle = self.createButton("Треугольник", 770, 740)
        self.pushButtonCircle = self.createButton("Круг", 770, 780)
        self.pushButtonRect = self.createButton("Прямоугольник", 770, 820)

        self.robot = RobotControl()
        self.robot.connect()
        self.robot.engage()

        # Назначения точек по цвету
        self.destinations = {
            "Красный": [100, 100, 100],
            "Зелёный": [200, 100, 100],
            "Синий": [300, 100, 100],
        }

        # Поток видео
        self.videoThread = threading.Thread(target=self.detect_objects)
        self.videoThread.daemon = True
        self.videoThread.start()

    def createButton(self, text, x, y):
        button = QtWidgets.QPushButton(self.centralwidget)
        button.setGeometry(QtCore.QRect(x, y, 100, 30))
        button.setText(text)
        return button

    def log(self, text):
        self.textEditLog.append(text)
        with open("log.txt", "a") as f:
            f.write(text + "\n")

    def detect_objects(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Маски по цветам
            masks = {
                "Красный": cv2.inRange(hsv, (0, 120, 70), (10, 255, 255)),
                "Зелёный": cv2.inRange(hsv, (36, 50, 70), (89, 255, 255)),
                "Синий": cv2.inRange(hsv, (90, 50, 70), (128, 255, 255)),
            }

            for color, mask in masks.items():
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
                    x, y, w, h = cv2.boundingRect(approx)

                    if w * h < 1000:
                        continue

                    shape = ""
                    if len(approx) == 3:
                        shape = "Треугольник"
                        self.pushButtonTriangle.setStyleSheet("background-color: yellow")
                    elif len(approx) == 4:
                        aspect_ratio = float(w) / h
                        if 0.95 <= aspect_ratio <= 1.05:
                            shape = "Квадрат"
                            self.pushButtonSquare.setStyleSheet("background-color: yellow")
                        else:
                            shape = "Прямоугольник"
                            self.pushButtonRect.setStyleSheet("background-color: yellow")
                    elif len(approx) > 4:
                        shape = "Круг"
                        self.pushButtonCircle.setStyleSheet("background-color: yellow")

                    # Цветовая индикация
                    if color == "Красный":
                        self.pushButtonRed.setStyleSheet("background-color: red")
                    elif color == "Зелёный":
                        self.pushButtonGreen.setStyleSheet("background-color: green")
                    elif color == "Синий":
                        self.pushButtonBlue.setStyleSheet("background-color: blue")

                    self.log(f"Обнаружен {shape} цвета {color}")

                    # Автоматическое перемещение
                    dest = self.destinations.get(color)
                    self.robot.moveL([x, y, 150])
                    self.robot.controlGripper(True)
                    time.sleep(1)
                    self.robot.moveL(dest)
                    self.robot.controlGripper(False)
                    time.sleep(1)

            cv2.waitKey(1)
