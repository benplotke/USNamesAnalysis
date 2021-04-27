import os
import pandas
from get_life_tables import OUT_DIRECTORY


def _html_to_csv(in_path: str) -> None:
    out_path = in_path.rstrip('.html') + '.csv'
    with open(in_path, 'r') as file:
        all_tables = pandas.read_html(file)
        table = all_tables[1]
        table.columns = table.columns.droplevel(-1)
        table = table[[('Male', 'lx'), ('Female', 'lx')]]
        table.columns = ['M', 'F']
        table = table.dropna()
        table = table.reset_index(drop=True)
        table.applymap(lambda x: x/1e5)
        table.to_csv(out_path)


for f_name in os.listdir(OUT_DIRECTORY):
    path = os.path.join(OUT_DIRECTORY, f_name)
    if os.path.isfile(path) and path.endswith('.html'):
        _html_to_csv(path)
