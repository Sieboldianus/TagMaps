#!/usr/bin/env python
# coding: utf-8
# test tag clusters


# test_capitalize.py

def capital_case(x):
    return x.capitalize()

def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'