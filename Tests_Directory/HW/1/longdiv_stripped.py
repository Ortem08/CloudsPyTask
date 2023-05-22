#!/usr/bin/env python3


def long_division(dividend, divider):
    """
    Вернуть строку с процедурой деления «уголком» чисел dividend и divider.
    Формат вывода приведён на примерах ниже.

    Примеры:
    >>> 12345÷25
    12345|25
    100  |493
     234
     225
       95
       75
       20

    >>> 1234÷1423
    1234|1423
    1234|0

    >>> 24600÷123
    24600|123
    246  |200
      0

    >>> 246001÷123
    246001|123
    246   |2000
         1
    """

    quot = str(dividend // divider)
    str_div = str(dividend)
    div_len = len(str_div)
    lines = []
    last_str_indent = 0
    result = ""

    for i in range(len(quot)):
        lines.append(f"{int(quot[i]) * divider}{'*' * (len(quot) - i - 1)}")

    result += f"{dividend}|{divider}\n"
    if quot == '0':
        result += f"{dividend}|{quot}".rstrip()
        return result

    result += f"{lines[0].replace('*', ' ')}|{quot}".rstrip() + '\n'
    remainder = str(dividend - int(lines[0].replace('*', '0')))

    for i in range(1, len(lines)):
        if int(remainder) == 0:
            last_str_indent = lines[i-1].count('*')
            break
        if int(lines[i].replace('*', ' ')) == 0:
            continue

        offset_rem = remainder.rjust(div_len)
        end_mult = lines[i].rjust(div_len).find('*')

        if end_mult == -1:
            end_part = len(offset_rem)
        else:
            end_part = end_mult

        result += f"{offset_rem[:end_part]}{' ' * (len(offset_rem) - end_part)}".rjust(div_len).rstrip() + '\n'
        result += f"{lines[i].rjust(div_len).replace('*', ' ').rstrip()}\n"
        remainder = str(int(remainder) - int(lines[i].replace('*', '0')))

    result += (remainder + ' ' * last_str_indent).rjust(div_len).rstrip()
    return result


def main():
    print(long_division(123, 123))
    print()
    print(long_division(1, 1))
    print()
    print(long_division(15, 3))
    print()
    print(long_division(3, 15))
    print()
    print(long_division(12345, 25))
    print()
    print(long_division(1234, 1423))
    print()
    print(long_division(87654532, 1))
    print()
    print(long_division(24600, 123))
    print()
    print(long_division(4567, 1234567))
    print()
    print(long_division(246001, 123))
    print()
    print(long_division(100000, 50))
    print()
    print(long_division(123456789, 531))
    print()
    print(long_division(425934261694251, 12345678))


if __name__ == '__main__':
    main()
