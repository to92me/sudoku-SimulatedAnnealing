from matplotlib import pyplot as plt


class PlotStats:
    list_x = []
    list_y = []

    @staticmethod
    def plot_lists(points_x, points_y, name_x, name_y, label):

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
