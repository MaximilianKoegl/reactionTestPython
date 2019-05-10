#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import os
import csv
import time
import datetime
import random
from PyQt5 import QtGui, QtWidgets, QtCore
from playsound import playsound


class ReactionTimeTest(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.counter = 0
        self.initSettings()
        self.initUI()

    def initSettings(self):
        self.settings = []
        self.pause = False
        self.start_time = 0
        # https://stackoverflow.com/questions/6142689/initialising-an-array-of-fixed-size-in-python
        self.results = [None] * 4
        task_settings = []

        if len(sys.argv) == 2:
            info_settings = open(sys.argv[1], "r")
            participant = info_settings.readline().partition(":")[2].strip()

            for char in info_settings.readline().partition(":")[2].split(","):
                task_settings.append([char[1], char[2]])

            time_between_signals_ms = info_settings.readline().partition(":")[2].strip()
            self.settings = [participant, task_settings, time_between_signals_ms]

        else:
            print("No file attached...")
            quit()

    def initUI(self):
        self.setGeometry(500, 350, 800, 400)
        self.setWindowTitle('Experiment')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.text = "Press F or J to start"
        self.show()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_J or ev.key() == QtCore.Qt.Key_F:

            if self.counter != 0:
                self.saveData(ev.text())
                self.outputCSV()
                self.checkForEnd()

            self.counter += 1
            self.waitProcess()
            self.update()
            self.setTimer()
            self.setDistraction(self.settings[1][self.counter - 1][1])


    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)

        if self.counter == 0:
            self.drawText(event, qp)
        elif self.counter != 0 and not self.pause:
            trial = self.settings[1][self.counter-1]
            self.drawStimulus(event, qp, trial[0])


        qp.end()


    def waitProcess(self):
        self.pause = True
        self.update()
        # https://python-forum.io/Thread-PyQt-label-doesn-t-update-on-each-iteration
        QtGui.QGuiApplication.processEvents()
        time.sleep(int(self.settings[2]) / 1000)
        self.pause = False

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Decorative', 50))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def drawStimulus(self, event, qp, param):
        # https://stackoverflow.com/questions/6824681/get-a-random-boolean-in-python
        self.random_bool = bool(random.getrandbits(1))

        if param == "A":

            if self.random_bool:
                stimulus_info = "Blue Rectangle"
                qp.setBrush(QtGui.QColor(34, 34, 200))

            else:
                stimulus_info = "Red Rectangle"
                qp.setBrush(QtGui.QColor(200, 34, 34))

            rect = QtCore.QRect(350, 150, 100, 100)
            qp.drawRoundedRect(rect, 10.0, 10.0)

        else:
            stimulus_info = self.getEquation()
            qp.setPen(QtGui.QColor(0, 0, 0))
            qp.setFont(QtGui.QFont('Decorative', 50))
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, stimulus_info)

        self.results[0] = stimulus_info

    def getEquation(self):
        x = random.randrange(1, 10, 1)
        y = random.randrange(1, 10, 1)
        operators = [' + ', ' * ', ' - ', ' / ']
        chosen_operator = operators[random.randrange(0, 3, 1)]

        equation = str(x) + chosen_operator + str(y)
        res = eval(equation)

        if not self.random_bool:
            new_res = res

            while res == new_res:
                res = random.randrange(-20, 20, 1)

        return equation + " = " + str(res)

    def setDistraction(self, param):
        if param == "D":
            # https://stackoverflow.com/questions/16573051/sound-alarm-when-code-finishes
            playsound("sound.wav")


    def setTimer(self):
        self.start_time = time.time()

    def saveData(self, input):
        if (input == "f" and self.random_bool) or \
                (input == "j" and not self.random_bool):
            right_button = True

        else:
            right_button = False

        self.results[1] = input
        self.results[2] = right_button
        self.results[3] = time.time() - self.start_time

    def checkForEnd(self):
        if self.counter == len(self.settings[1]):
            quit()

    def outputCSV(self):
        res = [self.settings[0], self.results[0], self.settings[1][self.counter-1][0],
               self.settings[1][self.counter-1][1], self.results[1],  self.results[2],
               self.results[3], datetime.datetime.now()]

        if not os.path.isfile("./reaction_time_results.csv"):
            # https://realpython.com/python-csv/
            with open('reaction_time_results.csv', 'w', newline='') as result_file:
                fieldnames = [
                    'Participant_ID',
                    'Presented_Stimulus',
                    'Mental_Complexity',
                    'Distraction_Given',
                    'Key_Pressed',
                    'Right_Key_Chosen',
                    'Reaction_Time',
                    'Timestamp'
                ]
                file_writer = csv.DictWriter(result_file, fieldnames=fieldnames)
                file_writer.writeheader()
                file_writer.writerow({fieldnames[0]: res[0],
                                      fieldnames[1]: res[1],
                                      fieldnames[2]: res[2],
                                      fieldnames[3]: res[3],
                                      fieldnames[4]: res[4],
                                      fieldnames[5]: res[5],
                                      fieldnames[6]: res[6],
                                      fieldnames[7]: res[7]})
        else:
            # https://stackoverflow.com/questions/2363731/append-new-row-to-old-csv-file-python
            with open('reaction_time_results.csv', 'a') as result_file:
                fields = res
                file_writer = csv.writer(result_file)
                file_writer.writerow(fields)


def main():
    app = QtWidgets.QApplication(sys.argv)
    reaction_time_test = ReactionTimeTest()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
