import datetime
import matplotlib
import matplotlib.dates as dates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn

seaborn.set()


class Grapher(FigureCanvas):
    def __init__(self, valuefunction, endtime, ctime):
        self.times = []
        self.values = []
        self.ctime = ctime
        self.endtime = endtime
        self.get_value = valuefunction
        figure = plt.figure()
        figure.set_facecolor("None")
        super().__init__(figure)
        self.setStyleSheet("background-color: transparent;")

    def set_time(self, time):
        self.ctime = time

    def reset(self, ctime, endtime=None):
        self.times = []
        self.values = []
        self.ctime = ctime
        self.figure.clf()
        if endtime is not None:
            self.endtime = endtime

    def plotinfo(self):
        minute, second = divmod((self.endtime.second() - self.ctime.second()) +
                                (self.endtime.minute() - self.ctime.minute()) * 60, 60)
        if minute < 0:
            minute = 0
        fakedate = datetime.datetime.now().replace(minute=minute, second=second)
        time_mpl = matplotlib.dates.date2num(fakedate)
        if minute + second > 0:
            self.times.append(time_mpl)
            self.values.append(self.get_value())
        ax = plt.gca()
        ticks = self.get_ticks(fakedate)
        ax.set_xlim(ticks[0], ticks[-1])
        ax.xaxis.set_major_formatter(dates.DateFormatter("%M:%S"))
        if ax.get_ylim()[1] < 60:
            ax.set_ylim(0, 60)
        elif self.get_value() >= 60 and (self.get_value() > ax.get_ylim()[1]):
            ax.set_ylim(0, self.get_value() + 5)
        plt.ylabel("WPM")
        plt.plot_date(self.times, self.values, "b")
        self.update_plot()

    def get_ticks(self, date):
        totalseconds = self.endtime.second() + self.endtime.minute() * 60
        ticks = []
        for i in range(0, (totalseconds // 10) + 1):
            minutes, seconds = divmod((totalseconds // (totalseconds // 10)) * i, 60)
            ticks.append(date.replace(minute=minutes, second=seconds))
        return ticks

    def update_plot(self):
        self.draw()
