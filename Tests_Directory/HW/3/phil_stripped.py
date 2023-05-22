#!/usr/bin/env python3


import re
import queue
from urllib.parse import unquote

try:
    import httpx
except ModuleNotFoundError:
    import pip

    pip.main(['install', '--quiet', 'httpx'])
    import httpx


# для обращения к веб-странице можно использовать
# примеры https://www.python-httpx.org

def get_content(name):
    """
    Функция возвращает содержимое вики-страницы name из русской Википедии.
    В случае ошибки загрузки или отсутствия страницы возвращается None.
    """
    site = httpx.get('http://ru.wikipedia.org/wiki/' + name,
                     follow_redirects=True)
    if site.status_code == 200:
        return site.text
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
    for i in range(len(links)):
        links[i] = unquote(links[i])
    return list(set(links))


def find_chain(start, finish):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """
    visited = {}
    q = queue.Queue()
    q.put((start, None))

    if get_content(start) is None:
        return None

    while not q.empty():
        (current_link, previous) = q.get()
        visited[current_link] = previous

        article = get_content(current_link)
        indexes = extract_content(article)
        links = extract_links(article, indexes[0], indexes[1])

        for link in links:
            if link == finish:
                visited[finish] = current_link
                result = [finish]
                element = finish
                while element != start:
                    element = visited[element]
                    result.append(element)
                result.reverse()
                return result
            if link in visited:
                continue
            q.put((link, current_link))


def main():
    print(find_chain("Архимед", "Функция_(математика)"))


if __name__ == '__main__':
    main()
