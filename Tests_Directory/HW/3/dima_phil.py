#!/usr/bin/env python3
import queue
import re
from urllib.parse import unquote

try:
    import httpx
except ModuleNotFoundError:
    import pip

    pip.main(['install', '--quiet', 'httpx'])
    import httpx


def get_content(name):
    """
    Функция возвращает содержимое вики-страницы name из русской Википедии.
    В случае ошибки загрузки или отсутствия страницы возвращается None.
    """
    r = httpx.get('https://ru.wikipedia.org/wiki/' + name,
                  follow_redirects=True)

    if r.status_code == 200:
        return unquote(r.text)

    return None


def extract_content(page):
    """
    Функция принимает на вход содержимое страницы и возвращает 2-элементный
    tuple, первый элемент которого — номер позиции, с которой начинается
    содержимое статьи, второй элемент — номер позиции, на котором заканчивается
    содержимое статьи.
    Если содержимое отсутствует, возвращается (0, 0).
    """
    indexes = (0, 0)
    start = page.find(r'<body')
    end = page.find(r'</body>')
    if start > 0:
        indexes = (start, end)
    return indexes


def extract_links(page, begin, end):
    """
    Функция принимает на вход содержимое страницы и начало и конец интервала,
    задающего позицию содержимого статьи на странице и возвращает все имеющиеся
    ссылки на другие вики-страницы без повторений и с учётом регистра.
    """
    links = re.findall(r'(?<=[Hh]ref=[\'\"]/wiki/)[^\'\"#:]+(?=[\'\"])',
                       page[begin:end])
    return list(set(links))


def find_chain(start, finish):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """

    visited = dict()
    to_open = queue.Queue()
    to_open.put((start, ''))
    if get_content(start) is None:
        return None
    while True:
        link_to_open, prev = to_open.get()
        visited[link_to_open] = prev

        #        print(link_to_open)
        page = get_content(link_to_open)
        indexes = extract_content(page)
        links = extract_links(page, indexes[0], indexes[1])

        for link in links:
            if link == finish:
                visited[finish] = link_to_open
                break
            if link in visited:
                continue
            to_open.put((link, link_to_open))
        if finish in visited:
            break

    jumps = [finish]
    current = finish
    while current != start:
        current = visited[current]
        jumps.insert(0, current)

    return jumps


def main():
    print(find_chain("Архимед", "Функция_(математика)"))


if __name__ == '__main__':
    main()