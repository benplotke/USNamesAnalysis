import matplotlib.pyplot as plt

# Size of plots. Used to calculate size of display for plot matrices
DEFAULT_WIDTH = 6.4
DEFAULT_HEIGHT = 4.8


class Plot:

    def __init__(self, X, Y, xlabel=None, ylabel=None, title=None, display='plot'):
        self.X = X
        self.Y = Y
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.display = display

    def plot(self, axn):
        if self.display == 'plot':
            axn.plot(self.X, self.Y)
        elif self.display == 'bar':
            axn.bar(self.X, self.Y)
            axn.set_xticklabels(self.X, rotation='vertical')
        axn.set_xlabel(self.xlabel)
        axn.set_ylabel(self.ylabel)
        axn.set_title(self.title)


def display_jagged_matrix(matrix):
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


def save_jagged_matrix(matrix, fname):
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