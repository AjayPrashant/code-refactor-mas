```
import unittest
from math import pi

class TestGreetings(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet('Alice'), 'Hello Alice!')
        self.assertEqual(greet('Bob'), 'Hello Bob!')
        self.assertEqual(greet('Charlie'), 'Hello Charlie!')

class TestArea(unittest.TestCase):
    def test_calc_area(self):
        self.assertEqual(calc_area(3), pi * 9)
        self.assertEqual(calc_area(4), pi * 16)
        self.assertEqual(calc_area(5), pi * 25)

class TestIsEven(unittest.TestCase):
    def test_is_even(self):
        self.assertTrue(is_even(0))
        self.assertTrue(is_even(2))
        self.assertFalse(is_even(1))
        self.assertFalse(is_even(3))
        self.assertFalse(is_even(4))

class TestAllEven(unittest.TestCase):
    def test_all_even(self):
        self.assertTrue(all_even([2, 4, 6, 8]))
        self.assertFalse(all_even([3, 5, 7, 9]))
```
# Pytest Tests:
```
import pytest
from math import pi

def test_greet():
    assert greet('Alice') == 'Hello Alice!'
    assert greet('Bob') == 'Hello Bob!'
    assert greet('Charlie') == 'Hello Charlie!'

def test_calc_area():
    assert calc_area(3) == pi * 9
    assert calc_area(4) == pi * 16
    assert calc_area(5) == pi * 25

def test_is_even():
    assert is_even(0)
    assert is_even(2)
    assert not is_even(1)
    assert not is_even(3)
    assert not is_even(4)

def test_all_even():
    assert all_even([2, 4, 6, 8])
    assert not all_even([3, 5, 7, 9])
```