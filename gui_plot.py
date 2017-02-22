from matplotlib import pyplot as plt


class PlotStats:


    def __init__(self):
        self.list_x = []
        self.list_y = []
        self.plot_label = ""
        self.x_label = ""
        self.y_label = ""
        self.legend_label = ""
        self.color = 'b'

    def plot_lists(self, points_x, points_y, name_x, name_y, label):

        plt.plot(points_x, points_y, color='g', label=label)

        plt.xlabel(name_x)
        plt.ylabel(name_y)
        plt.title(label)

        plt.legend()
        plt.show()

    def add_x(self, x):
        self.list_x.append(x)

    def add_y(self, y):
        self.list_y.append(y)

    def plot(self, name_x, name_y, label):

        plt.plot(self.list_x, self.list_y, color='g', label=label)

        plt.xlabel(name_x)
        plt.ylabel(name_y)
        plt.title(label)

        plt.legend()
        plt.show()

    def clear(self):
        self.list_x.clear()
        self.list_x.clear()

    def plot_value_x_time_y(self):
        time = list(range(len(self.list_x)))

        plt.plot(time, self.list_x, color=self.color )

        plt.xlabel("time")
        plt.ylabel(self.y_label)
        plt.title(self.plot_label)

        plt.legend()
        plt.show()

        input()

    def update_plot(self):
        plt.draw()