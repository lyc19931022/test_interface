# coding=utf8
# __author__ = 'lyc'
"""
定义数据比较方法
1.CompareParam 是对外的参数比较类
2.compare_code 是关键参数值的比较办法,compare_params_complete是参数完整性的比较办法
3.get_compare_params 是获得返回包数据去重后集合的方法
4.recur_params 递归操作方法，辅助去重
"""
import json
from common.opmysql import OperationDbInterface
from common.Log import MyLog


class CompareParam(object):
    def __init__(self, params_interface):
        """
        初始化数据
        :param params_interface: 接口请求参数
        """
        self.params_interface = params_interface  # 接口入参
        self.id_case = params_interface.get('id')  # 测试用例ID
        self.result_list_response = []  # 定义用来存储 参数集的空列表
        self.params_to_compare = params_interface.get('params_to_compare')  # 定义参数完整性的预期结果

        self.db = OperationDbInterface()

    def compare_code(self, result_interface):
        """

        :param result_interface: HTTP返回数据包
        :return: 返回码Code，返回信息message,数据data
        """
        try:
            if isinstance(result_interface, str) and result_interface.startswith('{'):
                temp_result_interface = json.loads(result_interface)  # 将字符类型转换为字典类型
                temp_code_to_compare = self.params_interface.get('code_to_compare')
                if temp_code_to_compare in temp_result_interface.keys():
                    if str(temp_result_interface.get(temp_code_to_compare)) == str(
                            self.params_interface.get('code_expect')):
                        result = {'code': '0000', 'message': '关键字参数值相同', 'data': []}
                        self.db.op_sql("UPDATE case_interface set code_actual='%s',"
                                       "result_code_compare =%s where id =%s"
                                       % (temp_result_interface.get(temp_code_to_compare), 1, self.id_case))
                    elif str(temp_result_interface.get(temp_code_to_compare)) != str(
                            self.params_interface.get('code_expect')):
                        result = {'code': '1003', 'message': '关键字参数值不相同', 'data': []}
                        self.db.op_sql("UPDATE case_interface set code_actual='%s',"
                                       "result_code_compare =%s where id =%s"
                                       % (temp_result_interface.get(temp_code_to_compare), 0, self.id_case))
                    else:
                        result = {'code': '1002', 'message': '关键字参数值比较出错', 'data': []}
                        self.db.op_sql("UPDATE case_interface set code_actual='%s',"
                                       "result_code_compare =%s where id =%s"
                                       % (temp_result_interface.get(temp_code_to_compare), 3, self.id_case))
                else:
                    result = {'code': '1001', 'message': '返回包数据无关键字参数', 'data': []}
                    self.db.op_sql("UPDATE case_interface set result_code_compare =%s where id =%s"
                                   % (2, self.id_case))
            else:
                result = {'code': '1000', 'message': '返回包格式不合法', 'data': []}
                self.db.op_sql("UPDATE case_interface set result_code_compare =%s where id =%s"
                               % (4, self.id_case))

        except Exception as e:
            result = {'code': '9999', 'message': '关键字参数值比较异常', 'data': []}
            self.db.op_sql("UPDATE case_interface set result_code_compare =%s where id =%s"
                           % (9, self.id_case))

            MyLog.error(e)
        finally:
            return result

    def get_compare_params(self, result_interface):
        """

        :param result_interface: HTTP返回包数据
        :return: 返回码code,返回信息message,数据data
        """
        try:
            if result_interface.startswith('{') and isinstance(result_interface, str):
                temp_result_interface = json.loads(result_interface)  # 将字符串类型转换为字典类型
                self.result_list_response = temp_result_interface.keys()
                result = {'code': '0000', 'message': '成功', 'data': self.result_list_response}
            else:
                result = {'code': '1000', 'message': '返回包格式不合法', 'data': self.result_list_response}

        except Exception as e:
            result = {'code': '9999', 'message': '处理数据异常', 'data': []}
            MyLog.error(e)
        finally:
            return result

    def compare_params_complete(self, result_interface):
        """
        定义参数完整性的比较方法，将传参值与__recur_params 方法返回结果进行比较
        :param result_interface:
        :return: 返回码Code，返回信息Message,数据data
        """
        try:
            temp_compare_params = self.__recur_params__(result_interface)  # 获取返回包的参数集
            if temp_compare_params.get('code') == '0000':
                temp_result_list_response = temp_compare_params.get('data')  # 获取接口返回参数去重列表

                if self.params_to_compare.startswith('[') and isinstance(self.params_to_compare,
                                                                         str):  # 判断测试用例列表中预期结果集是否为列表
                    list_params_to_compare = eval(self.params_to_compare)  # 将数据库中的unicode编码数据转换为列表

                    if set(list_params_to_compare).issubset(set(temp_result_list_response)):  # 判断集合包含关系
                        result = {'code': '0000', 'message': '参数完整性比较一致', 'data': []}
                        self.db.op_sql("UPDATE case_interface set params_actual=\"%s\","
                                       "result_params_compare =%s where id =%s"
                                       % (temp_result_list_response, 1, self.id_case))
                    else:
                        result = {'code': '3001', 'message': '实际结果中元素不都在预期结果中', 'data': []}
                        self.db.op_sql("UPDATE case_interface set params_actual=\"%s\","
                                       "result_params_compare =%s where id =%s"
                                       % (temp_result_list_response, 0, self.id_case))
                else:
                    result = {'code': '4001', 'message': '用例中待比较参数集错误', 'data': self.params_to_compare}
            else:
                result = {'code': '2001', 'message': '调用__recur_params__方法返回错误', 'data': self.params_to_compare}
                self.db.op_sql("UPDATE case_interface set result_params_compare =%s where id =%s"
                               % (2, self.id_case))
        except Exception as e:
            result = {'code': '9999', 'message': '参数完整性比较异常', 'data': []}
            self.db.op_sql("UPDATE case_interface set result_params_compare =%s where id =%s"
                           % (9, self.id_case))
            MyLog.error(e)
        return result

    def __recur_params__(self, result_interface):
        """
        定义递归操作，将接口返回数据中的参数名写入列表中（去重）
        :return:
        """
        try:
            if isinstance(result_interface, str) and result_interface.startswith('{'):
                temp_result_interface = json.loads(result_interface)
                self.__recur_params__(temp_result_interface)
            elif isinstance(result_interface, dict):  # 入参是字典

                for param, value in result_interface.items():
                    self.result_list_response.append(param)
                    if isinstance(value, list):
                        for param in value:
                            self.__recur_params__(param)
                    elif isinstance(value, dict):
                        self.__recur_params__(value)
                    else:
                        continue
            else:
                pass
        except Exception as e:
            MyLog.error(e)
            result = {'code': '9999', 'message': '数据处理异常', 'data': []}
            return result
        return {'code': '0000', 'message': '成功', 'data': list(set(self.result_list_response))}


if __name__ == '__main__':
    sql = "select * from case_interface where  name_interface = 'getIpInfo.php' and id = 1"
    parma_interface = OperationDbInterface().select_one(sql)

    resul_interface = parma_interface.get('data').get('result_interface')
    test_compara_parma = CompareParam(parma_interface['data'])
    result_compare_params_complete = test_compara_parma.compare_params_complete(resul_interface)
    print(result_compare_params_complete)
