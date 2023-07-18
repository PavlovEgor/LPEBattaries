import pandas as pd
import numpy as np

batData = pd.read_csv(r'C:\Users\Дмитрий\PycharmProjects\pythonProject\Data\аккумуляторы электромобилей - Лист4.csv')
technical_specification = pd.read_csv(
    r'C:\Users\Дмитрий\PycharmProjects\pythonProject\Data\аккумуляторы электромобилей - ТЗ.csv')


def make_prod_from_str(string):
    return np.array(list(map(float, string.split('*')))).prod()


class Chaker:

    def __init__(self, bd, ts):
        self.batData = bd
        self.technical_specification = ts

    def quantity_in_series(self):
        n = self.technical_specification['Напряжение, В'] / self.batData['Вольтаж, В']
        return np.ceil(n)

    def quantity_in_parallel(self):
        n = self.technical_specification['Емкость, Ач'] / self.batData['Ёмкость, Ач']
        return np.ceil(n)

    def volume_of_cell(self):
        V = []
        for s in self.batData['Размеры,мм']:
            v = make_prod_from_str(s) * 1e-6
            V.append(v)
        return np.array(V)

    def mass(self):

        num_of_cells = self.quantity_in_parallel() * self.quantity_in_series()
        mass_of_cells = num_of_cells * self.batData['масса, кг']
        return mass_of_cells < self.technical_specification['Масса полной батареи, кг']

    def size(self):

        if self.technical_specification['Габариты сборки/\nбатареи, мм'] is None:
            return np.array([True] * len(self.batData['Производитель']))

        num_of_cells = self.quantity_in_parallel() * self.quantity_in_series()
        volume_of_cells = num_of_cells * self.volume_of_cell()
        ts_volume = make_prod_from_str(self.technical_specification['Габариты сборки/\nбатареи, мм'])
        return volume_of_cells < ts_volume

    def live_time(self):
        if self.technical_specification['Количество циклов \nна заряд/разряд'] is None:
            return np.array([True] * len(self.batData['Производитель']))

        return self.batData['Количество циклов \nна заряд/разряд'] > \
            self.technical_specification['Количество циклов \nна заряд/разряд']

    def long_current_of_discharging(self):
        if self.technical_specification['Длительный ток\nразряда, А'] is None:
            return np.array([True] * len(self.batData['Производитель']))

        return self.batData['Длительный ток\nразряда, А'] > \
            self.technical_specification['Длительный ток\nразряда, А']

    def long_current_of_charging(self):
        if self.technical_specification['Длительный ток\nзаряда, А'] is None:
            return np.array([True] * len(self.batData['Производитель']))

        return self.batData['Длительный ток\nзаряда, А'] > \
            self.technical_specification['Длительный ток\nзаряда, А']

    def fast_current_of_discharging(self):
        if self.technical_specification['Максимальный ток\r\nразряда, А'] is None:
            return np.array([True] * len(self.batData['Производитель']))

        return self.batData['Максимальный ток\r\nразряда, А'] > \
            self.technical_specification['Максимальный ток\r\nразряда, А']

    def fast_current_of_charging(self):
        if self.technical_specification['Максимальный ток\nзаряда, А'] is None:
            return np.array([True] * len(self.batData['Производитель']))

        return self.batData['Максимальный ток\nзаряда, А'] > \
            self.technical_specification['Максимальный ток\nзаряда, А']


