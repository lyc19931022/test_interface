# coding=utf8
"""
封装http操作
1.http_request是主方法，直接供外部调用
2.__http_get、__http_post是实际底层分类调用的方法
"""
import requests
from common import opmysql
import traceback
import ast
from common.Log import MyLog
from common.opmysql import OperationDbInterface
import traceback
import sys


class RequestInterface(object):
    @staticmethod
    def __new__param(param):
        try:
            if isinstance(param, str) and param.startswith('{'):
                new_param = eval(param)
            elif param is None:
                new_param = ''
            else:
                new_param = param
        except Exception as e:
            new_param = ''
            MyLog.error(e)
        return new_param

    def __http_post(self, interface_url, headerdata, interface_param):
        """

        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_param: 接口请求参数
        :return: 字典形式结果
        """
        try:
            if interface_url != '':
                temp_interface_param = self.__new__param(interface_param)
                response = requests.post(url=interface_url,
                                         headers=headerdata,
                                         data=temp_interface_param,
                                         verify=False,
                                         timeout=10)
                if response.status_code == 200:
                    response_time = response.elapsed.microseconds / 1000  # 发起请求和响应到达的时间,单位ms
                    result = {'code': '0000', 'message': '成功', 'data': response.text, 'response_time': response_time}
                else:
                    result = {'code': '2004', 'message': '接口返回状态错误', 'data': []}
            elif interface_url == '':
                result = {'code': '2002', 'message': '接口地址参数为空', 'data': []}
            else:
                result = {'code': '2003', 'message': '接口地址错误', 'data': []}
        except Exception as e:
            result = {'code': '9999', 'message': '系统异常', 'data': []}
            MyLog.error(e)
        return result

    def __http_get(self, interface_url, headerdata, interface_param):
        """

        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_param: 接口请求参数
        :return: 字典形式结果
        """
        try:
            if interface_url != '':
                temp_interface_param = self.__new__param(interface_param)
                if interface_url.endswith('?'):
                    requrl = interface_url + temp_interface_param
                else:
                    requrl = interface_url + '?' + temp_interface_param
                response = requests.get(url=requrl,
                                        headers=headerdata,
                                        verify=False,
                                        timeout=10)
                if response.status_code == 200:
                    response_time = response.elapsed.microseconds / 1000  # 发起请求和响应到达的时间,单位ms
                    result = {'code': '0000', 'message': '成功', 'data': response.text, 'response_time': response_time}
                else:
                    result = {'code': '3004', 'message': '接口返回状态错误', 'data': []}
            elif interface_url == '':
                result = {'code': '3002', 'message': '接口地址参数为空', 'data': []}
            else:
                result = {'code': '3003', 'message': '接口地址错误', 'data': []}
        except Exception as e:
            result = {'code': '9999', 'message': '系统异常', 'data': []}
            MyLog.error(e)
        return result

    def http_request(self, interface_url, headerdata, interface_parm, request_type):
        """

        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_parm: 接口请求参数
        :param request_type: 请求类型
        :return: 字典形式结果
        """
        try:
            if request_type == 'get' or request_type == 'GET':
                result = self.__http_get(interface_url,
                                         headerdata,
                                         interface_parm)
            elif request_type == 'post' or request_type == 'POST':
                result = self.__http_post(interface_url,
                                          headerdata,
                                          interface_parm)
            else:
                result = {'code': '1000', 'message': '请求类型错误', 'data': []}
        except Exception as e:
            traceback.print_exc()
            MyLog.error(e)
        return result


if __name__ == '__main__':
    test_interface = RequestInterface()
    obj = OperationDbInterface(host_db='127.0.0.1', user_db='root', pwd_db='123456', name_db='test_interface',
                               port_db=3306,
                               link_type=0)
    sen_sql = "SELECT exe_mode,url_interface,header_interface,params_interface,code_expect from case_interface WHERE name_interface='getIpInfo.php' AND id=1; "
    parmams_interface = obj.select_one(sen_sql)

    print(parmams_interface)
    if parmams_interface.get('code') == '0000':
        # print(parmams_interface)
        url_interface = parmams_interface.get('data').get('url_interface')
        # print(url_interface)
        headdata = ast.literal_eval(parmams_interface.get('data').get('header_interface')) #将unicode转换为字典
        type_interface = parmams_interface.get('data').get('exe_mode')
        # print((headdata))
        if url_interface!='' and headdata !='' and parmams_interface!='' and type_interface!='':
            print('yes')
            result = test_interface.http_request(url_interface,headdata,parmams_interface.get('data').get('params_interface'),type_interface)
            print(result)


