import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from my_types import vector

# Size of plots. Used to calculate size of display for plot matrices
DEFAULT_WIDTH = 6.4
DEFAULT_HEIGHT = 4.8


class Plot:

    def __init__(self, X: vector, Y: vector, xlabel: str = None, ylabel: str = None, title: str = None,
                 display: str = 'plot'):
        self.X = X
        self.Y = Y
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.display = display

    def plot(self, ax: Axes) -> None:
        if self.display == 'plot':
            ax.plot(self.X, self.Y)
        elif self.display == 'bar':
            ax.bar(self.X, self.Y)
            ax.set_xticklabels(self.X, rotation='vertical')
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.title)


def display_jagged_matrix(matrix: list[list[Plot]]) -> None:
    h = len(matrix)
    w = max([len(row) for row in matrix])
    fig, axs = plt.subplots(h, w)
    for i, row in enumerate(matrix):
        for j, col in enumerate(row):
            col.plot(axs[i, j])
    fig.set_figwidth(w * DEFAULT_WIDTH)
    fig.set_figheight(h * DEFAULT_HEIGHT)
    plt.tight_layout()
    plt.show()


def save_jagged_matrix(matrix: list[list[Plot]], fname: str) -> None:
    h = len(matrix)
    w = max([len(row) for row in matrix])
    fig, axs = plt.subplots(h, w)
    for i, row in enumerate(matrix):
        for j, col in enumerate(row):
            col.plot(axs[i, j])
    fig.set_figwidth(w * DEFAULT_WIDTH)
    fig.set_figheight(h * DEFAULT_HEIGHT)
    plt.tight_layout()
    plt.savefig(fname)
