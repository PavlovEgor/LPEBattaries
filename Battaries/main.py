import pandas as pd
import numpy as np

batData = pd.read_csv(r'C:\Users\Дмитрий\PycharmProjects\pythonProject\Data\аккумуляторы электромобилей - Лист4.csv')
technical_specification = pd.read_csv(
    r'C:\Users\Дмитрий\PycharmProjects\pythonProject\Data\аккумуляторы электромобилей - ТЗ.csv')


def make_prod_from_str(string, form):  # расчет объема ячейки исходя их формы в мм3
    if form == 'призматическая' or form == 'pouch':  # для призматических и пауч запись в файле длина*высота*толщина
        return np.array(list(map(float, string.split('*')))).prod()
    if form == 'цилиндрическая':  # для цилиндрических запись: диаметр * высота
        D, h = list(map(float, string.split('*')))
        return np.pi * h * (D / 2) ** 2

class Chaker:

    def __init__(self, bd, ts):
        self.batData = bd  # информация о всех доступных ячейках
        self.technical_specification = ts  # техническое задание от заказчика

    def quantity_in_series(self):  # расчет количества ячеек в последовательности по напряжению в ТЗ и вольтажу ячейки
        n = self.technical_specification['Напряжение, В'].values / self.batData['Вольтаж, В'].values
        return np.ceil(n)

    def quantity_in_parallel(self):  # расчет количества ячеек в параллели по емкости в ТЗ и емкости ячейки
        n = self.technical_specification['Емкость, Ач'].values / self.batData['Ёмкость, Ач'].values
        return np.ceil(n)

    def volume_of_cell(self):  # расчет объемов ячеек в литрах
        V = []
        for s in self.batData['Размеры,мм']:
            v = make_prod_from_str(s) * 1e-6
            V.append(v)
        return np.array(V)

    def mass(self):  # проверка общей массы ячеек по ТЗ

        if self.technical_specification['Масса полной батареи, кг'].isnull().values[0]:  # проверка на наличие ТЗ
            return np.array([True] * len(self.batData['Производитель']))  # Если нет ТЗ, то подходят все ячейки

        num_of_cells = self.quantity_in_parallel() * self.quantity_in_series()
        mass_of_cells = num_of_cells * self.batData['масса, кг']
        return np.array(mass_of_cells) < float(self.technical_specification['Масса полной батареи, кг'].iloc[0])

    def size(self):

        if self.technical_specification['Габариты сборки/\nбатареи, мм'].isnull().values[0]:  # проверка на наличие ТЗ
            return np.array([True] * len(self.batData['Производитель']))  # Если нет ТЗ, то подходят все ячейки

        num_of_cells = self.quantity_in_parallel() * self.quantity_in_series()
        volume_of_cells = num_of_cells * self.volume_of_cell()
        ts_volume = make_prod_from_str(self.technical_specification['Габариты сборки/\nбатареи, мм'].values[0], 'призматическая')
        return np.array(volume_of_cells) < ts_volume

    def standart_check_req(self, nameOfParam, k=1):  # проверка того, что параметр ячейки больше его параметра в ТЗ
        if self.technical_specification[nameOfParam].isnull().values[0]:
            return np.array([True] * len(self.batData['Производитель']))

        return np.array(self.batData[nameOfParam]) * k > float(self.technical_specification[nameOfParam].iloc[0])

    def live_time(self):  # проверяет количество циклов на заряд/разряд ячейки и тз
        return self.standart_check_req('Количество циклов на заряд/разряд')

    def long_current_of_discharging(self):  # проверяет ток всей сборки и по тз
        return self.standart_check_req('Длительный ток разряда, А', self.quantity_in_parallel())

    def long_current_of_charging(self):
        return self.standart_check_req('Длительный ток заряда, А', self.quantity_in_parallel())

    def fast_current_of_discharging(self):
        return self.standart_check_req('Максимальный ток разряда, А', self.quantity_in_parallel())

    def fast_current_of_charging(self):
        return self.standart_check_req('Максимальный ток заряда, А', self.quantity_in_parallel())

    def standart_check_eq(self, nameOfParam):  # проверка того, что параметр ячейки равен его параметру в ТЗ
        if self.technical_specification[nameOfParam].isnull().values[0]:
            return np.array([True] * len(self.batData['Производитель']))

        return np.array(self.batData[nameOfParam]) == np.array(self.technical_specification[nameOfParam])

    def chemistry(self):  # если в тз задана химия катода сравнивает ее с ячейкой
        return self.standart_check_eq('Электрохимическая система')

    def form_factor(self):  # если в тз задан форм-фактор сравнивает ее с ячейкой
        return self.standart_check_eq('Формфактор')


ts = technical_specification[1:2]  # берем любое ТЗ из имеющихся
Model = Chaker(batData, ts)
Answer = pd.DataFrame({
    'Производитель': batData['Производитель'].values,
    'модель': batData['модель'].values,
    'Электрохимическая система': Model.chemistry(),
    'Формфактор': Model.form_factor(),
    'Габариты сборки/\nбатареи, мм': Model.size(),
    'Масса полной батареи, кг': Model.mass(),
    'Количество циклов \nна заряд/разряд': Model.live_time(),
    'Длительный ток разряда, А': Model.long_current_of_discharging(),
    'Длительный ток заряда, А': Model.long_current_of_charging(),
    'Максимальный ток разряда, А': Model.fast_current_of_discharging(),
    'Максимальный ток заряда, А': Model.fast_current_of_charging(),
})


AT = Answer.T
R = []
for i in range(len(Answer.index)):
    r = np.array(AT[i][2:], dtype=int).sum()
    R.append(r)
Answer['Рейтинг по совпадениям'] = R
Answer = Answer.sort_values(by='Рейтинг по совпадениям', ascending=False)

Answer.to_csv('Answer.csv')
