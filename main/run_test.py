from common.opmysql import OperationDbInterface
from common.request import RequestInterface
from common.cache import extraDB
from common.Log import MyLog
from common.compare import CompareParam
from cacheout import Cache
import time
import ast


class Run(object):
    def __init__(self):
        self.db = OperationDbInterface()
        self.cases_to_run = []
        self.cache = Cache(maxsize=256, ttl=0, timer=time.time)

    def get_all_cases(self):
        """
        获取所有测试用例
        :return: []
        """
        sql = 'select * from case_interface'
        print(self.db.select_all(sql))

    def get_one_case(self, condition):
        """
        获取一条测试用例
        :return: []
        """

    def get_cases_for_run(self):
        """
        获取要执行的测试用例
        :return:
        """
        pass

    def execute_test_case(self, *arg):
        """
        执行测试用例
        :param arg:
        :return:
        """
        test_interface = RequestInterface()
        sql = "SELECT * FROM `case_interface` WHERE case_status = 1"
        result = self.db.select_all(sql)
        if result.get('code') == '0000' and result.get('data'):
            MyLog.debug('获取执行接口成功')
            datas = result.get('data')
            for temp_case_interface in datas:
                obj = extraDB(temp_case_interface, self.cache)
                params_interface = obj.replace()  # 执行测试前重构测试数据
                url_interface = params_interface.get('url_interface')
                id_case = temp_case_interface.get('id')
                name_interface = temp_case_interface.get('name_interface')
                name_case = temp_case_interface.get('name_case')
                headdata = ast.literal_eval(params_interface.get('header_interface'))
                type_interface = params_interface.get('exe_mode')
                if url_interface != '' and headdata != '' and type_interface != '':
                    temp_level_check = temp_case_interface.get('check_level')  # 检查级别

                    result_http_respones = test_interface.http_request(url_interface, headdata,
                                                                       params_interface.get('params_interface'),
                                                                       type_interface)
                    print(result_http_respones)
                    MyLog.debug("用例返回消息:{result}".format(result=result_http_respones.get('data')))
                    obj.setvar(result_http_respones.get('data'))
                    self.db.op_sql("UPDATE case_interface  SET result_interface = '%s' where id = %s " %
                                   (result_http_respones.get('data'), id_case))  # 将返回包数据写入用例表

                    if result_http_respones['code'] == '0000' and len(result_http_respones['data']) != 0:
                        base_compare = CompareParam(temp_case_interface)
                        if '0' in list(temp_level_check):  # 执行关键值参数检查
                            result_compare_code = base_compare.compare_code(result_http_respones.get('data'))
                            MyLog.debug('用例编号：%s|检查级别：关键字参数值|接口名称：%s|用例名称：%s|提示信息:%s \n'
                                        % (id_case, name_interface, name_case, result_compare_code['message']))
                        if '1' in list(temp_level_check):  # 执行参数完整性检查
                            result_compare_params_complete = base_compare.compare_params_complete(
                                result_http_respones.get('data'))
                            MyLog.debug('用例编号：%s|检查级别：参数完整性|接口名称：%s|用例名称：%s|提示信息:%s \n'
                                        % (id_case, name_interface, name_case, result_compare_params_complete['message']))
                    elif len(result_http_respones['data']) == 0:
                        MyLog.debug('接口名称： %s|信息错误：获取用例数据为空，请检查用例\n' % name_interface)
                    else:
                        MyLog.debug('接口名称： %s|信息错误：获取用例数据失败' % name_interface)


if __name__ == '__main__':
    Run().execute_test_case()
