import plotter
from timelines import get_timelines, TimelineCollection
import os


if __debug__:
    PLOT_DIRECTORY = 'regression_plots'
else:
    PLOT_DIRECTORY = 'plots'


def plot_name_frequency_histogram(timelines: TimelineCollection, fname: str) -> None:

    print('Generating top ten histograms')

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
            plot = plotter.Plot(X, Y, title=title, display='bar')

            babes.append(plot)

        matrix.append(babes)

    plotter.save_jagged_matrix(matrix, fname)


def plot_top_names_count_proportion_derivative(timelines: TimelineCollection, fname: str) -> None:

    print('Generating top count plots')

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
            plot = plotter.Plot(years, counts, title=f'{name_pos.name} top from {name_pos.start_year} till {name_pos.end_year}')
            count_plots.append(plot)
            years, proportions = timelines.get_name_proportion_over_time(name_pos.name)
            plot = plotter.Plot(years, proportions, title=f'{name_pos.name} proportions')
            proportion_plots.append(plot)
            years, derivatives = timelines.get_name_proportion_derivative(name_pos.name, smooth)
            plot = plotter.Plot(years, derivatives, f'{name_pos.name} proportion derivative')
            derivative_plots.append(plot)

        matrix.append(count_plots)
        matrix.append(proportion_plots)
        matrix.append(derivative_plots)

    plotter.save_jagged_matrix(matrix, fname)


def plot_top_derivative_names(timelines: TimelineCollection, fname: str) -> None:

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
            plot = plotter.Plot(years, counts, title=f'{name.name} counts')
            count_plots.append(plot)
            years, proportions = timelines.get_name_proportion_over_time(name)
            plot = plotter.Plot(years, proportions, title=f'{name.name} proportions')
            proportion_plots.append(plot)
            years, derivatives = timelines.get_name_proportion_derivative(name, smooth)
            plot = plotter.Plot(years, derivatives, title=f'{name.name} proportion derivative')
            derivative_plots.append(plot)

        matrix.append(count_plots)
        matrix.append(proportion_plots)
        matrix.append(derivative_plots)

    plotter.save_jagged_matrix(matrix, fname)


def plot_commonality_quantiles_by_decade(timelines: TimelineCollection, granularity: int, fname: str) -> None:

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
            plot = plotter.Plot(X, Y, title=title, display='bar')
            row.append(plot)
        matrix.append(row)

    plotter.save_jagged_matrix(matrix, fname)


timelines = get_timelines()

if not os.path.exists(PLOT_DIRECTORY):
    os.makedirs(PLOT_DIRECTORY)

file_name = 'top_names_count_proportion_and_derivative_matrix.png'
path = os.path.join(PLOT_DIRECTORY, file_name)
plot_top_names_count_proportion_derivative(timelines, path)

file_name = 'historgram_top_10_names_by_decade.png'
path = os.path.join(PLOT_DIRECTORY, file_name)
plot_name_frequency_histogram(timelines, path)

file_name = 'top_10_derivatives.png'
path = os.path.join(PLOT_DIRECTORY, file_name)
plot_top_derivative_names(timelines, path)

file_name = 'commonality_distribution_by_decade.png'
path = os.path.join(PLOT_DIRECTORY, file_name)
plot_commonality_quantiles_by_decade(timelines, 100, path)
