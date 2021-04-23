
import regex
import os
import heapq
import matplotlib.pyplot as plt
from random import shuffle

DEFAULT_WIDTH = 6.4
DEFAULT_HEIGHT = 4.8

# ToDo

# Possible analysis
#   - list most unisex names
#   - add name combining
#   - predict next top name
#   - calculate expected age


# smooth - the points to the left and to the right to average
def derivative(X, Y, smooth=0):
    dX = []
    dY = []
    for i in range(1, len(X)):
        dX.append(X[i])
        delta = Y[i] - Y[i-1]
        dY.append(delta)

    Ysmooth = []
    for i in range(smooth, len(dX)-smooth):
        y = sum( dY[ i-smooth : i+smooth ] ) / ( 2*smooth + 1 )
        Ysmooth.append(y)
    Xsmooth = dX[ smooth : len(dX) - smooth ]

    return (Xsmooth, Ysmooth)


def list_to_quantiles(l, granularity, fold=sum):
    steps = granularity * [len(l)//granularity]
    remainder = len(l)%granularity
    for i in range(remainder):
        steps[i] += 1
    shuffle(steps)
    i = 0
    quantiles = []
    for step in steps:
        quantiles.append( fold( l[i: i + step]) )
        i += step
    return quantiles


class InfiniteZeroedList:

    def __init__(self, default):
        self.list = {}
        self.min_idx = None
        self.max_idx = None
        self.default = default

    def __getitem__(self, idx):
        if idx in self.list:
            return self.list[idx]
        return self.default

    def __delitem__(self, idx):
        if idx in self.list:
            del self.list[idx]
        if self.list:
            if self.min_idx == idx:
                while not self.min_idx in self.list:
                    self.min_idx += 1
            elif self.max_idx == idx:
                while not self.max_idx in self.list:
                    self.max_idx += 1

    def __setitem__(self, idx, value):
        self.list[idx] = value
        if self.min_idx is None or self.min_idx > idx:
            self.min_idx = idx
        if self.max_idx is None or self.max_idx < idx:
            self.max_idx = idx

    def __iter__(self):
        return iter(self.list.values())

    def __str__(self):
        return str(self.list)


class Name:

    def __init__(self, name, sex):
        self.name = name
        self.sex = sex

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return isinstance(other, Name) and self.name == other.name and self.sex == other.sex

    def __hash__(self):
        return hash((self.name, self.sex))

    def __str__(self):
        return f'{self.name}, {self.sex}'


class NameYearData:

    def __init__(self, count):
        self.count = count
        self.rank = -1
        self.proportion = -1

    def __bool__(self):
        return self.count > 0


class NameTimeline:

    def __init__(self, name):
        self.name = name
        self.yearToCount = InfiniteZeroedList(NameYearData(0))
        self.size = 0

    def __str__(self):
        return f'{self.name}: {self.yearToCount}'

    def __getitem__(self, year):
        return self.yearToCount[year]

    def __delitem__(self, year):
        count = self.yearToCount[year]
        del self.yearToCount[year]
        if self.size == count:
            self.size = max(self.yearToCount)

    def __setitem__(self, year, data):
        if isinstance(data, NameYearData):
            self.yearToCount[year] = data
        elif self.yearToCount[year]:
            self.yearToCount[year].count = data
        else:
            self.yearToCount[year] = NameYearData(data)
        
        if self.yearToCount[year].count > self.size:
            self.size = self.yearToCount[year].count

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.size < other.size
        return False

    def __iter__(self):
        self.min = self.get_first_year()
        self.max = self.get_last_year()
        self.year = self.min
        return self

    def __next__(self):
        if self.year <= self.max:
            val = (self.year, self.yearToCount[self.year])
            self.year += 1
            return val
        raise StopIteration

    def get_first_year(self):
        first_year = self.yearToCount.min_idx
        return first_year

    def get_last_year(self):
        return self.yearToCount.max_idx


class NamePosition:

    def __init__(self, name, start_year=None, end_year=None):
        self.name = name
        self.start_year = start_year
        self.end_year = end_year


class TimelineCollection:

    def __init__(self):
        self.timelines = {}
        self.year_to_male_total = {}
        self.year_to_female_total = {}
        self.first_year = -1
        self.last_year = -1

    @classmethod
    def load_names(cls, dir_name):

        names = cls()
        years = []

        for file_name in os.listdir(dir_name):

            if not file_name.endswith(".txt"):
                continue

            file_path = os.path.join(dir_name, file_name)
            year = int(regex.search('yob(\d{4})\.txt', file_name)[1])
            years.append(year)

            with open(file_path, 'r') as file:
                for line in file:
                    line = line.rstrip("\n")
                    line = line.split(",")
                    name, sex, count = line
                    name = Name(name, sex)
                    count = int(count)
                    names._add_name_year_count(name, year, count)
                    names._add_year_count(sex, year, count)

        names.first_year = min(years)
        names.last_year = max(years)

        return names

    def _add_year_count(self, sex, year, count):
        if sex == 'M':
            if not year in self.year_to_male_total:
                self.year_to_male_total[year] = 0
            self.year_to_male_total[year] += count
        if sex == 'F':
            if not year in self.year_to_female_total:
                self.year_to_female_total[year] = 0
            self.year_to_female_total[year] += count

    def _add_name_year_count(self, name, year, count):
        if not name in self.timelines:
            self.timelines[name] = NameTimeline(name)
        self.timelines[name][year] = count

    def get_total_for_era(self, start_year, end_year, sex):
        total = 0
        for year in range(start_year, end_year):
            if sex == 'M':
                total += self.year_to_male_total[year]
            elif sex == 'F':
                total += self.year_to_female_total[year]
        return total

    def get_top_counts_names_for_era(self, start_year, end_year, sex, name_count):
        top_names = []
        for t in self.timelines.values():
            if sex != t.name.sex:
                continue
            count = 0
            for year in range(start_year, end_year):
                count += t[year].count
            name = t.name
            if len(top_names) < name_count:
                heapq.heappush(top_names, (count, name))
            else:
                heapq.heappushpop(top_names, (count, name))
        return heapq.nlargest(name_count, top_names)

    def get_n_top_derivative_names(self, sex, name_count, smooth=0):
        top_names = []
        for t in self.timelines.values():
            if sex != t.name.sex:
                continue
            years, derivatives = self.get_name_proportion_derivative(t.name, smooth)
            if not derivatives:
                continue
            top_increase = max(derivatives)
            name = t.name
            if len(top_names) < name_count:
                heapq.heappush(top_names, (top_increase, name))
            else:
                heapq.heappushpop(top_names, (top_increase, name))
        increase_names = heapq.nlargest(name_count, top_names)
        return [tupl[1] for tupl in increase_names]

    def get_top_names_for_era(self, start_year, end_year, sex, name_count):
        top_names = self.get_top_counts_names_for_era(start_year, end_year, sex, name_count)
        return [name[1] for name in top_names]

    def get_top_count_list(self, start_year, end_year, step, sex):
        top_names = []
        while start_year + step < end_year:
            name = self.get_top_names_for_era(start_year, start_year + step, sex, 1)[0]
            if top_names and top_names[-1].name == name:
                top_names[-1].end_year += step
            else:
                top_names.append(NamePosition(name, start_year, start_year + step))
            start_year += step
        return top_names

    def get_commonality_quantiles_for_era(self, start_year, end_year, granularity, sex):
        name_to_count = {}
        total = 0
        for name, timeline, in self.timelines.items():
            if name.sex != sex:
                continue
            for year in range(start_year, end_year):
                if timeline[year].count:
                    name_to_count[name] = name_to_count.get(name, 0) + timeline[year].count
                    total += timeline[year].count

        counts = [count for count in name_to_count.values()]
        counts.sort(reverse=True)
        quantiles = list_to_quantiles(counts, granularity)
        quantiles = [q/total for q in quantiles]
        return quantiles


    def get_timeline(self, name):
        if name in self.timelines:
            return self.timelines[name]
        return False

    def get_timelines(self):
        return list(self.timelines.values())

    def get_name_count_over_time(self, name):
        timeline = self.get_timeline(name)
        if not timeline:
            return
        years = []
        counts = []
        for year, data in timeline:
            years.append(year)
            counts.append(data.count)
        return (years, counts)

    def get_name_proportion_over_time(self, name):
        timeline = self.get_timeline(name)
        if not timeline:
            return
        years = []
        proportions = []
        for year, data in timeline:
            years.append(year)
            if name.sex == 'M':
                total = self.year_to_male_total[year]
            else:
                total = self.year_to_female_total[year]
            proportions.append(data.count/total)
        return (years, proportions)

    def get_name_proportion_derivative(self, name, smooth=0):
        X, Y = self.get_name_proportion_over_time(name)
        return derivative(X, Y, smooth)


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

    @staticmethod
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

    @staticmethod
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


    @classmethod
    def plot_name_frequency_histogram(cls, timelines, fname):

        print("Generating top ten histograms")

        matrix = []
        step = 10
        topN = 10
        first_year = timelines.first_year
        last_year = timelines.last_year

        for sex in ('M', 'F'):
            babes = []
            for start_year in range(first_year, last_year+1, step):
                end_year = start_year + step

                top_count_names = timelines.get_top_counts_names_for_era(start_year, end_year, sex, topN)
                total = timelines.get_total_for_era(start_year, end_year, sex)
                top_total = 0

                X = []
                Y = []
                for count, name in top_count_names:
                    X.append(name.name)
                    Y.append(count/total)
                    top_total += count
                percent_in_top = 100*top_total/total
                sex_word = 'boys' if sex == 'M' else 'girls'
                title = f'{percent_in_top:.2g}% {sex_word} had top {topN} names from {start_year} till {end_year}'
                plot = Plot(X, Y, title=title, display='bar')

                babes.append(plot)

            matrix.append(babes)

        cls.save_jagged_matrix(matrix, fname)


    @classmethod
    def plot_top_names_count_proportion_derivative(cls, timelines, fname):

        print("Generating top count plots")

        matrix = []
        first_year = timelines.first_year
        last_year = timelines.last_year
        smooth = 2

        for sex in ('M', 'F'):
            name_positions = timelines.get_top_count_list(first_year, last_year+1, 1, sex)
            count_plots = []
            proportion_plots = []
            derivative_plots = []
            for name_pos in name_positions:
                years, counts = timelines.get_name_count_over_time(name_pos.name)
                plot = Plot(years, counts, title=f'{name_pos.name} top from {name_pos.start_year} till {name_pos.end_year}')
                count_plots.append(plot)
                years, proportions = timelines.get_name_proportion_over_time(name_pos.name)
                plot = Plot(years, proportions, title=f'{name_pos.name} proportions')
                proportion_plots.append(plot)
                years, derivatives = timelines.get_name_proportion_derivative(name_pos.name, smooth)
                plot = Plot(years, derivatives, f'{name_pos.name} proportion derivative')
                derivative_plots.append(plot)

            matrix.append(count_plots)
            matrix.append(proportion_plots)
            matrix.append(derivative_plots)

        cls.save_jagged_matrix(matrix, fname)

    @classmethod
    def plot_top_derivative_names(cls, timelines, fname):

        matrix = []
        first_year = timelines.first_year
        last_year = timelines.last_year
        plot_count = 10
        smooth = 2

        for sex in ('M', 'F'):
            top_derivatives = timelines.get_n_top_derivative_names(sex, plot_count, smooth)

            count_plots = []
            proportion_plots = []
            derivative_plots = []

            for name in top_derivatives:
                years, counts = timelines.get_name_count_over_time(name)
                plot = Plot(years, counts, title=f'{name.name} counts')
                count_plots.append(plot)
                years, proportions = timelines.get_name_proportion_over_time(name)
                plot = Plot(years, proportions, title=f'{name.name} proportions')
                proportion_plots.append(plot)
                years, derivatives = timelines.get_name_proportion_derivative(name, smooth)
                plot = Plot(years, derivatives, title=f'{name.name} proportion derivative')
                derivative_plots.append(plot)

            matrix.append(count_plots)
            matrix.append(proportion_plots)
            matrix.append(derivative_plots)

        cls.save_jagged_matrix(matrix, fname)


    @classmethod
    def plot_commonality_quantiles_by_decade(cls, timelines, granularity, fname):
        
        print('Generating name commonality preference histograms')

        matrix = []
        first_year = timelines.first_year
        last_year = timelines.last_year
        step = 10

        for sex in ('M', 'F'):
            row = []
            for start_year in range(first_year, last_year+1, step):
                Y = timelines.get_commonality_quantiles_for_era(start_year, start_year+step, granularity, sex)
                X = list(range(1,granularity+1))
                sex_word = 'boy' if sex == 'M' else 'girl'
                title = f'distribution of {sex_word} from {start_year} till {start_year+step}'
                plot = Plot(X, Y, title=title, display='bar')
                row.append(plot)
            matrix.append(row)

        cls.save_jagged_matrix(matrix, fname)


print("loading names")
timelines = TimelineCollection.load_names("USNames")

def repl(timelines):
    while True:
        name = input("Name: ")
        name = name[0].upper() + name[1:].lower()
        matrix = [[], []]
        for sex in ('M', 'F'):
            name_gender = Name(name, sex)
            years, counts = timelines.get_name_count_over_time(name_gender)
            if not counts:
                print(f'Name: {name}, Sex: {sex} not found.')
                continue
            pronoun = 'boys' if sex == 'M' else 'girls'
            count_plot = Plot(years, counts, title=f'Counts of {pronoun} named {name}')
            matrix[0].append(count_plot)
            years, proportions = timelines.get_name_proportion_over_time(name_gender)
            proportion_plot = Plot(years, proportions, title=f'Proportion of {pronoun} named {name}')
            matrix[1].append(proportion_plot)
        Plot.display_jagged_matrix(matrix)


#Plot.plot_top_names_count_proportion_derivative(timelines, 'regression.top_names_count_proportion_and_derivative_matrix.png')
#Plot.plot_name_frequency_histogram(timelines, 'regression.historgram_top_10_names_by_decade.png')
#Plot.plot_top_derivative_names(timelines, 'top_10_derivatives.png')
# Plot.plot_commonality_quantiles_by_decade(timelines, 100, 'commonality_distribution_by_decade.png')
repl(timelines)