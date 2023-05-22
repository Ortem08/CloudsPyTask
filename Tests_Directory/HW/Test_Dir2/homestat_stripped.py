#!/usr/bin/env python3
import re
import collections
from collections import Counter


def make_stat(filename):
    """
    Функция вычисляет статистику по именам за каждый год с учётом пола.
    """
    global all_males_count, all_females_count
    with open(filename, encoding='cp1251') as file:
        parts = re.split(r'(?<=<h3>)', file.read())
    parts.pop(0)

    years = []
    males = []
    females = []
    all_males = []
    all_females = []
    years_data = {}
    males_females = {}
    all_males_females = {}

    for part in parts:
        year = part[:4]
        years.append(year)
        all_names = re.split(r'(?<=/>)', part)
        all_names.pop(0)

        for line in all_names:
            name = re.search(r'\w+(?=</a)', line)[0]
            if name in ['Лёва', 'Илья', 'Никита'] \
                    or (name[-1] not in ['а', 'я'] and name != 'Любовь'):
                males.append(name)
                all_males.append(name)
            else:
                females.append(name)
                all_females.append(name)

        males_count = dict(Counter(males))
        females_count = dict(Counter(females))
        males_females['males'] = males_count
        males_females['females'] = females_count
        years_data[year] = males_females.copy()

        all_males_count = dict(Counter(all_males))
        all_females_count = dict(Counter(all_females))
        males.clear()
        females.clear()

    all_males_females['males'] = all_males_count
    all_males_females['females'] = all_females_count

    return [years_data, all_males_females]


def extract_years(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список годов,
    упорядоченный по возрастанию.
    """
    result = list(stat[0].keys())
    result.reverse()
    return result


def extract_general(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для всех имён.
    Список должен быть отсортирован по убыванию количества.
    """
    data = stat[1]
    combined = data['males'] | data['females']
    res = sorted(combined.items(), key=lambda x: x[1])
    res.reverse()
    return res


def extract_general_male(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён мальчиков.
    Список должен быть отсортирован по убыванию количества.
    """
    data = stat[1]['males']
    result = sorted(data.items(), key=lambda x: x[1])
    result.reverse()
    return result


def extract_general_female(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён девочек.
    Список должен быть отсортирован по убыванию количества.
    """
    data = stat[1]['females']
    result = sorted(data.items(), key=lambda x: x[1])
    result.reverse()
    return result


def extract_year(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    data = stat[0][year]
    res = data['males'] | data['females']
    res = sorted(res.items(), key=lambda x: x[1])
    res.reverse()
    return res


def extract_year_male(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён мальчиков в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    data = stat[0][year]['males']
    result = sorted(data.items(), key=lambda x: x[1])
    result.reverse()
    return result


def extract_year_female(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён девочек в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    data = stat[0][year]['females']
    result = sorted(data.items(), key=lambda x: x[1])
    result.reverse()
    return result


if __name__ == '__main__':
    pass
