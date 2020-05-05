#!/usr/bin/env python3

# This file takes a list of newline-separated KB/MB/GB/etc values
# and will sum them in KB.

#

import sys
import unittest
from typing import List

conversions = {
    'k': 1E3,  # kilo
    'm': 1E6,  # mega
    'g': 1E9,  # giga
    't': 1E12,  # tera
    'p': 1E15,  # peta
}


def sum_si_bytes(l: List[str]) -> float:
    """Sum a list of strings that are SI byte-suffixed values."""

    total = 0

    for line in l:
        total += (normalize_si_bytes_number(line))

    return total


def normalize_si_bytes_number(num: str) -> float:
    """
    :param num: a number in the format 1234.34MB
    :return: Its size in bytes.
    """
    # Lowercase, remove 'b', remove whitespace.
    num = num.lower().replace('b', '').strip()

    # print("Line: " + num)

    # If the end of the line ends with an SI suffix,
    if num[-1] in list(conversions.keys()):
        # print("Wow! This line has " + num[-1] + " as a suffix!")

        number, suffix = float(num[:-1]), num[-1]

        # print(suffix,number)

        return conversions[suffix] * number

    # If the line is not k,m,g,t,etc, or digits,
    elif num[-1] not in '0123456789.':
        print("Unknown suffix '{}'".format(num[-1]))
        exit(1)
    else:
        # print("No suffix. Number is {}.".format(si_number))
        return float(num)


tc = unittest.TestCase()
tc.assertEqual(normalize_si_bytes_number('100.01'), 100.01)
tc.assertEqual(normalize_si_bytes_number('1.01k'), (1.01 * 1E3))
tc.assertEqual(normalize_si_bytes_number('12MB'), (12.0 * 1E6))

tc.assertEqual(
    sum_si_bytes([
        '100.01', '1.01k', '12MB'
    ]),
    sum([100.01, (1.01 * 1E3), (12.0 * 1E6)])
)

if __name__ == '__main__':
    print(sum_si_bytes(sys.stdin))
