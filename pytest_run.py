# coding=utf8
# import re
import pytest
import allure
from common.opmysql import OperationDbInterface
# from common.analyse import AnalyseData
from common.request import RequestInterface
from common.compare import CompareParam
# from public import config
from common.Log import MyLog

cases_list = []  # 测试用例集,里面放tuple[(name_interface1,case1),(name_interface2,case2)]
base_request = RequestInterface()
base_db = OperationDbInterface()

module_execute = base_db.select_all("SELECT value_config from config_total "
                                    "WHERE key_config = 'exe_setup' and `status` = 1")  # 获取待执行接口数据
if len(module_execute.get('data')) != 0 and module_execute.get('code') == '0000':
    for module_execute_one in module_execute.get('data'):
        temp_module_execute = eval(module_execute_one.get('value_config'))
        for temp_name_interface, condition in temp_module_execute.items():
            # print("###########开始执行接口：%s############\n" % temp_name_interface)
            temp_level_check = condition.get('level_check')  # 检查级别
            temp_level_exe = tuple(condition.get('level_exe'))  # 执行级别
            data_case_interface = base_db.select_all("SELECT * FROM case_interface WHERE "
                                                     "case_status = 1 AND "
                                                     "name_interface =  '%s' AND exe_level in %s"
                                                     % (temp_name_interface, temp_level_exe))  # 获取接口测试数据

            if data_case_interface.get('code') == '0000' and len(data_case_interface.get('data')) != 0:
                for one_case in data_case_interface.get('data'): cases_list.append(
                    (one_case.get('name_interface'), one_case))

                @pytest.mark.parametrize('name_interface,case_interface', cases_list)
                @allure.title("{name_interface}")
                def test_pytest_api_run(name_interface, case_interface):
                    temp_case_interface = case_interface
                    # for temp_case_interface in data_case_interface.get('data'):
                    id_case = str(temp_case_interface.get('id'))  # 用例编号
                    url_interface = temp_case_interface.get('url_interface')  # 接口地址
                    headerdata = eval(temp_case_interface.get('header_interface'))  # 请求头文件
                    type_interface = temp_case_interface.get('exe_mode')  # 执行环境
                    param_interface = temp_case_interface.get('params_interface')  # 接口请求参数
                    # print('param_interface', param_interface)
                    result_http_respones = base_request.http_request(interface_url=url_interface,
                                                                     headerdata=headerdata,
                                                                     interface_parm=param_interface,
                                                                     request_type=type_interface)
                    # 发送http请求
                    print('接口地址', url_interface, '\n',
                          '请求参数', param_interface, '\n'
                                                   '返回包数据', result_http_respones)

                    base_db.op_sql("UPDATE case_interface  SET result_interface = '%s' where id = %s " %
                                   (result_http_respones.get('data'), id_case))  # 将返回包数据写入用例表

                    if result_http_respones['code'] == '0000' and len(result_http_respones['data']) != 0:
                        for child_level_check in temp_level_check:  # 循环检查级别
                            base_compare = CompareParam(temp_case_interface)
                            if child_level_check in (0,):  # 执行关键值参数检查
                                result_compare_code = base_compare.compare_code(
                                    result_http_respones.get('data'))
                                allure.attach('用例编号：%s|检查级别：关键字参数值|接口名称：%s|提示信息:%s \n'
                                      % (id_case, name_interface, result_compare_code['message']))
                                assert result_compare_code['code'] == '0000'

                            elif child_level_check in [1]:  # 执行参数完整性检查
                                result_compare_params_complete = base_compare.compare_params_complete(
                                    result_http_respones.get('data'))
                                allure.attach('用例编号：%s|检查级别：参数完整性|接口名称：%s|提示信息:%s \n'
                                      % (id_case, name_interface, result_compare_params_complete['message']))
                                assert result_compare_params_complete['code'] == '0000'
                            elif child_level_check in [2]:  # 执行功能测试，待开发
                                pass
                            elif child_level_check in [3]:  # 执行结构完整性检查,待开发
                                pass

                            else:
                                allure.attach('用例编号：%s|接口名称：%s|检查级别错误:%s\n'
                                      % (id_case, name_interface, child_level_check))
                        assert True

                    elif len(result_http_respones['data']) == 0:
                        allure.attach('接口名称： %s|信息错误：获取用例数据为空，请检查用例\n' % name_interface)
                        assert False
                    else:
                        allure.attach('接口名称： %s|信息错误：获取用例数据失败|错误信息： %s\n'
                              % (name_interface, data_case_interface['message']))
                        assert False
                        # print('#####################结束执行接口：%s#################### \n' % name_interface)
else:
    MyLog.error('错误信息：待执行接口获取失败|错误信息：%s' % module_execute['message'])

if __name__ == '__main__':
    import os

    pytest.main(['-s', '-q', 'pytest_run.py', '--alluredir', './result/'])
    os.system('allure serve ./result/')
