from common.request import RequestInterface
from exceloperation.readfromexcel import ReadFromExcel
from function.Built_in_functions import *
from common.Log import MyLog
from cacheout import Cache
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
        self.extra_key_list_str = params_interface.get('extra')
        # self.functions_tuple_list = []

    def setvar(self, result_interface):
        """

        :param result_interface: 接口返回参数
        :return:
        """

        if self.extra_key_list_str and \
                self.extra_key_list_str.startswith("[") and \
                self.extra_key_list_str.endswith("]"):
            try:
                extra_key_list = eval(self.extra_key_list_str)
            except Exception as e:
                MyLog.error(e)

            if result_interface and result_interface.startswith('{') and isinstance(result_interface, str):
                temp_result_interface = json.loads(result_interface)  # 将字符串类型转换为字典类型
                for extra_key in extra_key_list:
                    value_list = get_target_value(extra_key, temp_result_interface, tmp_list=[])
                    if len(value_list) == 1:
                        for value in value_list:
                            if isinstance(value, str):  # 判断value是否是字符串
                                self.cache.set(extra_key, '\'' + value + '\'')
                            elif isinstance(value, int):  # 判断value是不是int类型
                                self.cache.set(extra_key, value)
                            elif isinstance(value, dict):  # 判断value是不是字典类型
                                self.cache.set(extra_key, value)
                            else:
                                MyLog.error('未处理的数据类型', value)

                        MyLog.debug('接口返回值入参成功%s %s' % (extra_key, value))
                    elif len(value_list) == 0:
                        MyLog.error('缓存数据设置错误，未找到对应返回值%s' % extra_key)
                    elif len(value_list) > 1:
                        # MyLog.error('value_list',value_list)
                        MyLog.error('缓存数据设置错误，存在多个值')
            else:
                MyLog.error('接口返回值类型错误，无法将参数存入缓存')
        else:
            MyLog.debug('接口无缓存参数')

        # seslf.cache.set(key, value)

    def getvar(self):
        """
        获取参数
        :return:{key1:value1,key2:value2,...}
        """
        sign = self.match_var()
        cache_value = {}
        if sign:
            for key in sign:
                value = self.cache.get(key)
                if value is not None:
                    MyLog.debug('获取其他接口入参参数成功,参数名称为%s，参数值为%s' % (sign, value))
                    cache_value[key] = value
                    # return self.cache.get(sign)
                else:
                    MyLog.error('获取参数异常，缓存中没有%s的值' % sign)
            return cache_value
        else:
            MyLog.debug('该接口无${}标识')
            return None

    def get_function_return(self, functions_tuple_list):
        """
        :functions_tuple_dict: {'stradd': '12', 'sumadd': 3}
        :return: 返回内置函数计算结果，格式为list
         [{'function_name': 'stradd', 'result': '12'}, {'function_name': 'sumadd', 'result': 3}]
        """
        return_list = []
        kwargs = {}
        for function_name, function_arg in functions_tuple_list:
            functions_result_dict = {}
            args = function_arg.split(',')
            function_return = eval(function_name)(*args, **kwargs)
            functions_result_dict['function_name'] = function_name
            functions_result_dict['args'] = function_arg
            if isinstance(function_return, str):  # 判断函数返回值是否是字符串
                functions_result_dict['result'] = '\'' + function_return + '\''
            elif isinstance(function_return, int):
                functions_result_dict['result'] = function_return
            elif isinstance(function_return, dict):
                functions_result_dict['result'] = '\'' + function_return + '\''
            return_list.append(functions_result_dict)
        return return_list

    def match_var(self):
        """
        :return:查找含有$的字符${cache_id}或$cache_id输出为cache_id
        """
        sign = []
        pattern = r"\$\{(\w+)\}|\$(\w+)"
        for _k, _v in self.params_interface.items():
            if _v and isinstance(_v, str) and '$' in _v:
                result = re.findall(pattern, _v)
                if result:
                    for key_tuple in result:
                        for key in key_tuple:
                            if key: sign.append(key)
        if sign:
            return sign
        else:
            return None

    def match_function(self):
        """

        :return: 匹配含有${function(*arg)}的字符数组：[('test', '8,9'), ('sum', '1')]
        """

        functions_tuple_list = None
        pattern = r"\$\{(\w+)\(([\$\w\.\-/\s=,]*)\)\}"
        for _k, _v in self.params_interface.items():
            if _v and isinstance(_v, str) and '$' in _v and '(' in _v and ')' in _v:
                functions_tuple_list = re.findall(pattern, _v)

        if functions_tuple_list is not None:
            return functions_tuple_list
        else:
            return None

    def replace(self):
        """
        :return: 返回新赋值的字典
        """
        replace_dict = {}
        functions_tuple_list = self.match_function()

        if self.match_var() is None and functions_tuple_list is None:
            MyLog.debug('没有要替换的变量或函数返回值')
            return self.params_interface

        if self.match_var():  # 进行变量赋值替换
            params_interface_json = json.dumps(self.params_interface, ensure_ascii=False)
            _temp_json = params_interface_json
            _new_params_dict = self.getvar()
            for _k,_v in _new_params_dict.items():
                _temp_json = _temp_json.replace('$'+_k,_v)

            self.params_interface = json.loads(_temp_json)
            MyLog.debug('已进行变量赋值替换:%s' % self.params_interface)
        functions_tuple_list = self.match_function()
        print('functions_tuple_list',functions_tuple_list)

        if functions_tuple_list:
            function_results_dict = self.get_function_return(functions_tuple_list)
            params_interface_json = json.dumps(self.params_interface, ensure_ascii=False)
            print(function_results_dict)
            _temp_json = params_interface_json
            for need_to_replace_str in function_results_dict:
                _temp_json = _temp_json.replace(
                    '${'+need_to_replace_str['function_name'] + '(' + need_to_replace_str['args'] + ')'+'}',
                    str(need_to_replace_str['result']))
            self.params_interface = json.loads(_temp_json)
            MyLog.debug('已进行函数值赋值替换:%s' % self.params_interface)

        return self.params_interface


if __name__ == '__main__':
    cache = Cache(maxsize=256, ttl=0, timer=time.time)
    test_interface = RequestInterface()
    ex = ReadFromExcel(path=r"C:\Users\li\PycharmProjects\test_interface\Testcase\API_TestCases.xlsx")
    datas = ex.readsheet(sheet_name='queryphoneInfo')
    datas = datas['data']
    for i in range(len(datas)):
        obj = extraDB(datas[i], cache)
        params_interface = obj.replace()
        url_interface = params_interface.get('url_interface')

        headdata = ast.literal_eval(params_interface.get('header_interface'))
        type_interface = params_interface.get('exe_mode')
        if url_interface != '' and headdata != '' and type_interface != '':
            result = test_interface.http_request(url_interface, headdata,
                                                 params_interface.get('params_interface'), type_interface)
            print(result)
            obj.set(result.get('data'))
