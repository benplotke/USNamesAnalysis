from __future__ import annotations
from timelines import get_timelines, Name
from get_life_tables import OUT_DIRECTORY
from datetime import date
from regex import search
import os
import csv
from my_types import numeric


_life_table = None


class LifeTable:

    def __init__(self, male_map: dict[int, float], female_map: dict[int, float]):
        self.male_map = male_map
        self.female_map = female_map
        self.timelines = get_timelines()

    def __len__(self):
        return min(len(self.male_map), len(self.female_map))

    @staticmethod
    def _value_at_or_zero(l: list[numeric], index: int):
        if index < len(l):
            return l[index]
        return 0

    @classmethod
    def load_tables(cls) -> LifeTable:
        print('Loading life tables')
        current_year = date.today().year

        csv_tables = []
        all_names = [os.path.join(OUT_DIRECTORY, name) for name in os.listdir(OUT_DIRECTORY)]
        csv_names = [name for name in all_names if os.path.isfile(name) and name.endswith('.csv')]
        for csv_name in csv_names:
            start_year = int(search('.*(\d{4})\.csv', csv_name)[1])
            male = []
            female = []
            with open(csv_name, 'r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    male.append(float(row[1]))
                    female.append(float((row[2])))
            csv_tables.append((start_year, male, female))
        csv_tables.sort()

        step = csv_tables[1][0] - csv_tables[0][0]
        male_map = {}
        female_map = {}
        for table in csv_tables:
            start_year = table[0]
            male_col = table[1]
            female_col = table[2]
            for offset in range(step):
                birth_year = start_year + offset
                age = current_year - birth_year
                male_alive = cls._value_at_or_zero(male_col, age)
                female_alive = cls._value_at_or_zero(female_col, age)
                male_map[birth_year] = male_alive
                female_map[birth_year] = female_alive

        return LifeTable(male_map, female_map)

    def get_expected_age(self, name: Name) -> int:
        remain_map = self.male_map if name.sex == 'M' else self.female_map
        timeline = self.timelines.get_timeline(name)
        current_year = date.today().year
        start_year = current_year - len(self)
        ppl_count = 0
        name_years = 0
        for birth_year in range(1900, current_year):
            age = current_year - birth_year
            remaining = remain_map[birth_year] * timeline[birth_year].count
            ppl_count += remaining
            name_years += remaining * age
        return int(0.5 + name_years / ppl_count)


def get_life_table() -> LifeTable:
    global _life_table
    if not _life_table:
        _life_table = LifeTable.load_tables()
    return _life_table
