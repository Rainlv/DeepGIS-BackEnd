# !/usr/bin/env Python3
# -*- coding:utf-8 -*-
"""
 @FileName  :Singleton.py
 @Time      :2022/01/23 17:41
 @Author    :Xuanh.W
 @Usage     :
"""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


if __name__ == "__main__":
    pass
