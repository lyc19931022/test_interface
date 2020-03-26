from common.request import RequestInterface
from common.readfromexcel import ReadFromExcel
from cacheout import Cache
import string
import time
import ast
import json
import re


def get_target_value(key, dic, tmp_list=[]):
    """
    :param key: 目标key值
    :param dic: JSON数据
    :param tmp_list: 用于存储获取的数据
    :return: list
    """
    if not isinstance(dic, dict) or not isinstance(tmp_list, list):  # 对传入数据进行格式校验

        return 'argv[1] not an dict or argv[-1] not an list '

    if key in dic.keys():
        tmp_list.append(dic[key])  # 传入数据存在则存入tmp_list
    else:
        for value in dic.values():  # 传入数据不符合则对其value值进行遍历
            if isinstance(value, dict):
                get_target_value(key, value, tmp_list)  # 传入数据的value值是字典，则直接调用自身
            elif isinstance(value, (list, tuple)):
                _get_value(key, value, tmp_list)  # 传入数据的value值是列表或者元组，则调用_get_value
    return tmp_list


def _get_value(key, val, tmp_list):
    for val_ in val:
        if isinstance(val_, dict):
            get_target_value(key, val_, tmp_list)  # 传入数据的value值是字典，则调用get_target_value
        elif isinstance(val_, (list, tuple)):
            _get_value(key, val_, tmp_list)  # 传入数据的value值是列表或者元组，则调用自身


class extraDB(object):
    def __init__(self, params_interface, cache):
        """
        :param params_interface: 接口请求参数
        """
        self.cache = cache
        # self.cache = Cache(maxsize=256, ttl=0, timer=time.time)
        self.params_interface = params_interface
        self.extra_key = params_interface.get('extra')

    def set(self, result_interface):
        """

        :param result_interface: 接口返回参数
        :return:
        """
        if self.extra_key:
            print(self.extra_key)
            if result_interface and result_interface.startswith('{') and isinstance(result_interface, str):
                temp_result_interface = json.loads(result_interface)  # 将字符串类型转换为字典类型
                value_list = get_target_value(self.extra_key, temp_result_interface, tmp_list=[])
                if len(value_list) == 1:
                    for value in value_list: self.cache.set(self.extra_key, value)
                    print('接口返回值入参成功%s %s' % (self.extra_key, value))
                elif len(value_list)  == 0:
                    print('缓存数据设置错误，未找到对应返回值%s' % self.extra_key)
                elif len(value_list) > 1:
                    # print('value_list',value_list)
                    print('缓存数据设置错误，存在多个值')
            else:
                print('接口返回值类型错误，无法将参数存入缓存')
        else:
            print('接口无缓存参数')

        # seslf.cache.set(key, value)

    def get(self):
        """
        获取参数
        :return:
        """
        sign = self.match_sign()
        if sign:
            if self.cache.get(sign):
                print('获取其他接口入参参数成功,参数名称为%s，参数值为%s' % (sign, self.cache.get(sign)))
                return self.cache.get(sign)
            else:
                print('获取参数异常，缓存中没有%s的值' % sign)
        else:
            print('该接口无${}标识')
            return None

    def match_sign(self):
        """
        :return:查找含有$的字符{$cache_id}输出为cache_id
        """
        sign = None
        pattern = r"\$\{(\w+)\}|\$(\w+)"
        for _k, _v in self.params_interface.items():
            if _v and isinstance(_v, str) and '$' in _v:
                sign = re.findall(pattern, _v)[0][1]
        return sign

    def replace(self):
        """
        :return: 返回新赋值的字典
        """
        if self.match_sign():
            for _k, _v in self.params_interface.items():
                if _v and isinstance(_v, str) and '$' in _v:
                    _new_v = self.get()
                    _ = string.Template(_v)
                    self.params_interface[_k] = _.substitute({self.match_sign(): _new_v})  # 对字典进行重新赋值
            return self.params_interface
        else:
            print('该接口无${}标识，无需替换')
            return self.params_interface
            # return self.params_interface


if __name__ == '__main__':
    cache = Cache(maxsize=256, ttl=0, timer=time.time)
    test_interface = RequestInterface()
    ex = ReadFromExcel(path=r"C:\Users\li\PycharmProjects\test_interface\Testcase\API_TestCases.xlsx")
    datas = ex.readall(table_name='queryphoneInfo')
    for i in range(len(datas)):
        obj = extraDB(datas[i], cache)
        params_interface = obj.replace()
        print(params_interface)
        url_interface = params_interface.get('url_interface')

        headdata = ast.literal_eval(params_interface.get('header_interface'))
        type_interface = params_interface.get('exe_mode')
        if url_interface != '' and headdata != '' and type_interface != '':
            result = test_interface.http_request(url_interface, headdata,
                                                 params_interface.get('params_interface'), type_interface)
            obj.set(result.get('data'))
