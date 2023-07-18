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
        n = self.technical_specification['Напряжение, В'].values / self.batData['Вольтаж, В'].values
        return np.ceil(n)

    def quantity_in_parallel(self):
        n = self.technical_specification['Емкость, Ач'].values / self.batData['Ёмкость, Ач'].values
        return np.ceil(n)

    def volume_of_cell(self):
        V = []
        for s in self.batData['Размеры,мм']:
            v = make_prod_from_str(s) * 1e-6
            V.append(v)
        return np.array(V)

    def mass(self):

        if np.isnan(self.technical_specification['Масса полной батареи, кг'].values):
            print(self.technical_specification['Масса полной батареи, кг'].values)
            return np.array([True] * len(self.batData['Производитель']))

        num_of_cells = self.quantity_in_parallel() * self.quantity_in_series()
        mass_of_cells = num_of_cells * self.batData['масса, кг']
        return np.array(mass_of_cells) < float(self.technical_specification['Масса полной батареи, кг'].iloc[0])

    def size(self):

        if self.technical_specification['Габариты сборки/\nбатареи, мм'].isnull().values[0]:
            return np.array([True] * len(self.batData['Производитель']))

        num_of_cells = self.quantity_in_parallel() * self.quantity_in_series()
        volume_of_cells = num_of_cells * self.volume_of_cell()
        print(self.technical_specification['Габариты сборки/\nбатареи, мм'].isnull())
        ts_volume = make_prod_from_str(self.technical_specification['Габариты сборки/\nбатареи, мм'].values[0])

        return np.array(volume_of_cells) < ts_volume

    def standart_check_req(self, nameOfParam):
        if self.technical_specification[nameOfParam].isnull().values[0]:
            return np.array([True] * len(self.batData['Производитель']))
        return np.array(self.batData[nameOfParam]) > float(self.technical_specification[nameOfParam].iloc[0])

    def live_time(self):
        return self.standart_check_req('Количество циклов \nна заряд/разряд')

    def long_current_of_discharging(self):
        return self.standart_check_req('Длительный ток\nразряда, А')

    def long_current_of_charging(self):
        return self.standart_check_req('Длительный ток\nзаряда, А')

    def fast_current_of_discharging(self):
        return self.standart_check_req('Максимальный ток\r\nразряда, А')

    def fast_current_of_charging(self):
        return self.standart_check_req('Максимальный ток\nзаряда, А')

    def standart_check_eq(self, nameOfParam):
        if self.technical_specification[nameOfParam].isnull().values[0]:
            return np.array([True] * len(self.batData['Производитель']))

        return np.array(self.batData[nameOfParam]) == np.array(self.technical_specification[nameOfParam])

    def chemistry(self):
        return self.standart_check_eq('Электрохимическая система')

    def form_factor(self):
        return self.standart_check_eq('Формфактор')


ts = technical_specification[1:2]
Model = Chaker(batData, ts)
Answer = pd.DataFrame({
    'Производитель': batData['Производитель'].values,
    'модель': batData['модель'].values,
    'Электрохимическая система': Model.chemistry(),
    'Формфактор': Model.form_factor(),
    'Габариты сборки/\nбатареи, мм': Model.size(),
    'Масса полной батареи, кг': Model.mass(),
    'Количество циклов \nна заряд/разряд': Model.live_time(),
})
print(Answer)
Answer.to_csv('Answer.csv')
