import plotter
from timelines import get_timelines, Name


timelines = get_timelines()

while True:
    name = input('Name: ')
    name = name[0].upper() + name[1:].lower()
    matrix = [[], []]
    for sex in ('M', 'F'):
        name_gender = Name(name, sex)
        years, counts = timelines.get_name_count_over_time(name_gender)
        if not counts:
            print(f'Name: {name}, Sex: {sex} not found.')
            continue
        pronoun = 'boys' if sex == 'M' else 'girls'
        count_plot = plotter.Plot(years, counts, title=f'Counts of {pronoun} named {name}')
        matrix[0].append(count_plot)
        years, proportions = timelines.get_name_proportion_over_time(name_gender)
        proportion_plot = plotter.Plot(years, proportions, title=f'Proportion of {pronoun} named {name}')
        matrix[1].append(proportion_plot)
    plotter.display_jagged_matrix(matrix)
