# coding=utf8
# __author__ = 'lyc'
"""
定义数据比较方法
1.CompareParam 是对外的参数比较类
2.compare_code 是关键参数值的比较办法，compare_params_complete是参数完整性的比较办法
3.get_compare_params 是获得返回包数据去重后集合的方法
4.recur_params 递归操作方法，辅助去重
"""
import json
import os


class CompareParam(object):
    def __init__(self, params_interface):
        pass

    def compare_code(self, result_interface):
        pass

    def get_compare_params(self, result_interface):
        pass

    def compare_params_complete(self, result_interface):
        pass

    def __recur_params__(self):
        pass
