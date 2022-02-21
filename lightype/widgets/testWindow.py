from PyQt5.QtGui import QKeySequence, QPainter, QBrush
from PyQt5.QtWidgets import (QTextEdit, QWidget, QComboBox, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QPushButton,
                             QShortcut)
from PyQt5.QtCore import QEvent, QRectF, QSizeF, QPoint
from PyQt5.QtCore import (Qt, QTimer, QTime, pyqtSignal)

import lightype.corpusloader as corpusLoader
import lightype.widgets.grapher as grapher


class TestWindow(QWidget):
    def __init__(self):
        super(TestWindow, self).__init__()

        corpus = list(corpusLoader.Corpi.values())[0]
        vbox = QVBoxLayout()
        testPrompt = TypingTestPrompt(corpus)
        configBox = ConfigBox()
        infoBox = InfoBox(testPrompt, QTime.fromString(configBox.timeSelectDropdown.currentText(), "m:ss"))
        restartButton = QPushButton("Restart (Ctrl+R)")

        shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut.activated.connect(testPrompt.resetTest)
        shortcut.activated.connect(infoBox.resetGraph)

        configBox.corpusSelector.corpusChanged.connect(testPrompt.setCorpus)
        configBox.corpusSelector.corpusChanged.connect(infoBox.resetGraph)
        configBox.timeChanged.connect(infoBox.setTime)
        restartButton.clicked.connect(testPrompt.resetTest)
        restartButton.clicked.connect(infoBox.resetGraph)
        vbox.addWidget(configBox)
        vbox.addWidget(infoBox, 20)
        vbox.addWidget(restartButton, 10)
        vbox.addWidget(testPrompt, 5)
        self.setLayout(vbox)


class ConfigBox(QWidget):
    timeChanged = pyqtSignal(QTime)

    class CorpusDropdown(QWidget):
        corpusChanged = pyqtSignal(corpusLoader.Corpus)

        def __init__(self):
            super().__init__()
            self.dropdown = QComboBox()
            self.corpus_names = {}
            for corpus in corpusLoader.Corpi.values():
                self.dropdown.addItem(corpus.name)
                self.corpus_names[corpus.name] = corpus
            self.description = QLabel(self.corpus_names[self.dropdown.currentText()].description)
            self.dropdown.currentTextChanged.connect(self.option_chosen)
            vbox = QVBoxLayout()
            vbox.addWidget(self.dropdown)
            vbox.addWidget(self.description)
            self.setLayout(vbox)

        def option_chosen(self):
            corpus = self.corpus_names[self.dropdown.currentText()]
            self.description.setText(corpus.description)
            self.corpusChanged.emit(corpus)

    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        hbox = QHBoxLayout()

        self.corpusSelector = self.CorpusDropdown()
        self.timeSelectDropdown = QComboBox()
        self.timeSelectDropdown.addItem("1:00")
        self.timeSelectDropdown.addItem("3:00")
        self.timeSelectDropdown.addItem("5:00")
        self.timeSelectDropdown.addItem("10:00")
        self.timeSelectDropdown.addItem("0:30")
        self.timeSelectDropdown.currentTextChanged.connect(self.timeChange)

        hbox.addWidget(self.corpusSelector, Qt.AlignBottom)
        hbox.addWidget(self.timeSelectDropdown)
        self.setLayout(hbox)

    def timeChange(self, timeString):
        self.timeChanged.emit(QTime.fromString(timeString, "m:ss"))

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        rect = QRectF(QPoint(0, 0), QSizeF(self.size()))
        painter.fillRect(rect, QBrush(Qt.lightGray))
        super().paintEvent(event)


class InfoBox(QWidget):
    class Timer(QLabel):
        timerFinished = pyqtSignal()

        def __init__(self, start: QTime):
            super().__init__()
            self.startTime = start
            self.time = start
            self.setStyleSheet("font-weight: bold; font-size: 30px")
            self.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
            self.setText(self.time.toString())
            self.timer = QTimer()
            self.timer.timeout.connect(self.tick)

        def start(self):
            self.timer.start(1000)

        def tick(self):
            self.time = self.time.addSecs(-1)
            self.setText(self.time.toString())
            if self.time == QTime(0, 0):
                self.timer.stop()
                self.timerFinished.emit()

        def reset(self):
            self.timer.stop()
            self.time = self.startTime
            self.setText(self.time.toString())

    class Tracker(QWidget):
        def __init__(self, name, totrack):
            super().__init__()
            self.totrack = totrack
            layout = QVBoxLayout()
            self.tracker = QLabel(str(self.totrack()))
            name = QLabel(name)
            layout.addWidget(name)
            layout.addWidget(self.tracker, Qt.AlignHCenter)
            self.setStyleSheet("font-size: 12px")
            self.tracker.setStyleSheet("font-size: 12px")
            self.setLayout(layout)

        def update(self):
            self.tracker.setText(str(self.totrack()))

    def get_WPM(self):
        try:
            testseconds = (60 * self.timer.time.minute()) + self.timer.time.second()
            starttime = (60 * self.timer.startTime.minute()) + self.timer.startTime.second()
            wordscorrect = [word for word in self.testPrompt.wordscorrect if word]
            return int(round(len(wordscorrect) * (starttime / (starttime - testseconds))) // (starttime / 60))
        except ZeroDivisionError:
            return 0

    def get_CPM(self):
        try:
            testseconds = (60 * self.timer.time.minute()) + self.timer.time.second()
            starttime = (60 * self.timer.startTime.minute()) + self.timer.startTime.second()
            characters = [len(self.testPrompt.words[idx]) for (idx, word) in enumerate(self.testPrompt.wordscorrect) if
                          word]
            return int(round(sum(characters) * (starttime / (starttime - testseconds))) // (starttime / 60))
        except ZeroDivisionError:
            return 0

    def setTime(self, time: QTime):
        self.timer.startTime = time
        self.timer.reset()
        self.testPrompt.resetTest()
        self.resetGraph()

    def __init__(self, testPrompt, time: QTime):
        super(InfoBox, self).__init__()
        self.testPrompt = testPrompt
        vbox = QVBoxLayout()
        grid = QGridLayout()
        vbox.addLayout(grid)

        self.timer = self.Timer(time)

        self.WPMcounter = self.Tracker("WPM", self.get_WPM)
        grid.addWidget(self.WPMcounter)

        self.CPMcounter = self.Tracker("CPM", self.get_CPM)
        grid.addWidget(self.CPMcounter, 0, 1)

        self.WCorrectCounter = self.Tracker("Words Correct",
                                            lambda: len(
                                                [word for word in self.testPrompt.wordscorrect if word is True]))
        grid.addWidget(self.WCorrectCounter, 1, 0)

        self.WWrongCounter = self.Tracker("Words Incorrect",
                                          lambda: len(
                                              [word for word in self.testPrompt.wordscorrect if word is False]))
        grid.addWidget(self.WWrongCounter, 1, 1)

        self.timer.timerFinished.connect(testPrompt.freeze)
        self.testPrompt.typingStarted.connect(self.timer.start)
        self.testPrompt.testResetted.connect(self.timer.reset)
        self.timer.timer.timeout.connect(self.WPMcounter.update)
        self.timer.timer.timeout.connect(self.CPMcounter.update)
        self.timer.timer.timeout.connect(self.WCorrectCounter.update)
        self.timer.timer.timeout.connect(self.WWrongCounter.update)

        vbox.addWidget(self.timer, Qt.AlignHCenter)

        self.wpm_grapher = grapher.Grapher(self.get_WPM, self.timer.startTime, self.timer.time)
        self.wpm_grapher.plotinfo()
        self.timer.timer.timeout.connect(lambda: self.wpm_grapher.set_time(self.timer.time))
        self.timer.timer.timeout.connect(self.wpm_grapher.plotinfo)

        vbox.addWidget(self.wpm_grapher)
        self.setLayout(vbox)

    def resetGraph(self):
        self.wpm_grapher.reset(self.timer.startTime, self.timer.time)
        self.wpm_grapher.plotinfo()


class TypingTestPrompt(QTextEdit):
    typingStarted = pyqtSignal()
    testResetted = pyqtSignal()

    def __init__(self, corpus: corpusLoader.Corpus):
        super(TypingTestPrompt, self).__init__()

        self.installEventFilter(self)
        self.setOverwriteMode(True)
        self.corpus = corpus
        self.wordindex = 0
        self.currentChar = 0
        self.wordscorrect = []
        self.words = [getWord() for getWord in [corpus.getRandomWord] * 100]
        self.started = False
        self._populateWords()

    def _populateWords(self, index=None):
        if index is None:
            index = self.wordindex
        cursor = self.textCursor()
        position = cursor.position()
        cursor.movePosition(cursor.End)
        for idx in range(index, len(self.words)):
            cursor.insertHtml("<u><font color=\"#4bc9c1\" size=\"+2\">%s </font></u>" % self.words[idx])
        cursor.setPosition(position)
        self.setTextCursor(cursor)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if not self.started:
                self.typingStarted.emit()
                self.started = True
            if event.key() == Qt.Key_Backspace:
                return True
            if event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Down, Qt.Key_Up]:
                return True
            elif self.currentChar == len(self.words[self.wordindex]):
                try:
                    self.wordscorrect[self.wordindex]
                except IndexError:
                    self.wordscorrect.append(True)
                self.wordindex += 1
                self.currentChar = 0
                cursor = self.textCursor()
                cursor.setPosition(cursor.position() + 1)
                cursor.deletePreviousChar()
                cursor.insertText(" ")
                self.setTextCursor(cursor)
                return True
            elif event.text():
                if event.text() == " ":
                    return True
                cursor = self.textCursor()
                cursor.setPosition(cursor.position() + 1)
                cursor.deletePreviousChar()
                if self.words[self.wordindex][self.currentChar] == event.text():
                    cursor.insertHtml("<font color=\"Black\" size=\"+2\">%s</font>" % event.text())
                else:
                    self.wordscorrect.append(False)
                    cursor.insertHtml("<font color=\"Red\" size=\"+2\">%s</font>" % event.text())
                self.currentChar += 1
                if self.wordindex > len(self.words) / 2:
                    oldlength = len(self.words)
                    self.words.extend([getWord() for getWord in [self.corpus.getRandomWord] * 100])
                    self._populateWords(oldlength)
                return True
        return super(TypingTestPrompt, self).eventFilter(obj, event)

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        pass

    def grabMouse(self):
        pass

    def freeze(self):
        self.setDisabled(True)
        self.started = False
        self.setStyleSheet("background-color: #eeeeed")

    def resetTest(self):
        self.clear()
        self.wordindex = 0
        self.currentChar = 0
        self.wordscorrect = []
        self.words = [getWord() for getWord in [self.corpus.getRandomWord] * 100]
        self.started = False
        self.setDisabled(False)
        self._populateWords()
        self.testResetted.emit()

    def setCorpus(self, corpus):
        self.corpus = corpus
        self.resetTest()
