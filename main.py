# coding=utf8
import re
from common.opmysql import OperationDbInterface
from common.analyse import AnalyseData
from common.request import RequestInterface
from common.compare import CompareParam
from public import config
from common.Log import MyLog

if __name__ == '__main__':
    base_request = RequestInterface()
    base_db = OperationDbInterface()
    try:
        print("开始接口自动化程序,请选择操作类型（0|执行用例:1|导出测试结果）")
        value_input = str(input('请输出操作类型：'))
        while not re.search(r'^[0-1]$', value_input):
            print('请输入正确的操作类型（0|执行用例:1|导出测试结果）')
            value_input = str(input('请输出操作类型：'))
        else:
            if value_input == '0':
                print('你输入的是：0|执行测试用例')
                module_execute = base_db.select_all("SELECT value_config from config_total "
                                                    "WHERE key_config = 'exe_setup' and `status` = 1")  # 获取待执行接口数据

                if len(module_execute.get('data')) != 0 and module_execute.get('code') == '0000':
                    for module_execute_one in module_execute.get('data'):
                        temp_module_execute = eval(module_execute_one.get('value_config'))
                        for temp_name_interface, condition in temp_module_execute.items():
                            print("###########开始执行接口：%s############\n" % temp_name_interface)
                            temp_level_check = condition.get('level_check')  # 检查级别
                            temp_level_exe = tuple(condition.get('level_exe'))  # 执行级别
                            data_case_interface = base_db.select_all("SELECT * FROM case_interface WHERE "
                                                                     "case_status = 1 AND "
                                                                     "name_interface =  '%s' AND exe_level in %s"
                                                                     % (temp_name_interface, temp_level_exe))  # 获取接口测试数据
                            if data_case_interface.get('code') == '0000' and len(data_case_interface.get('data')) != 0:
                                for temp_case_interface in data_case_interface.get('data'):
                                    id_case = str(temp_case_interface.get('id'))  # 用例编号
                                    url_interface = temp_case_interface.get('url_interface')  # 接口地址
                                    headerdata = eval(temp_case_interface.get('header_interface'))  # 请求头文件
                                    type_interface = temp_case_interface.get('exe_mode')  # 执行环境
                                    param_interface = temp_case_interface.get('params_interface')  # 接口请求参数
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
                                                print('用例编号：%s|检查级别：关键字参数值|接口名称：%s|提示信息:%s \n'
                                                      % (id_case, temp_name_interface, result_compare_code['message']))
                                            elif child_level_check in [1]:  # 执行参数完整性检查
                                                result_compare_params_complete = base_compare.compare_params_complete(
                                                    result_http_respones.get('data'))
                                                print('用例编号：%s|检查级别：参数完整性|接口名称：%s|提示信息:%s \n'
                                                      % (id_case, temp_name_interface, result_compare_code['message']))
                                            elif child_level_check in [2]: #  执行功能测试，待开发
                                                pass
                                            elif child_level_check in [3]: #  执行结构完整性检查,待开发
                                                pass

                                            else:
                                                print('用例编号：%s|接口名称：%s|检查级别错误:%s\n'
                                                      % (id_case, temp_name_interface, child_level_check))
                                    elif len(result_http_respones['data']) == 0:
                                        print('接口名称： %s|信息错误：获取用例数据为空，请检查用例\n'%temp_name_interface)
                                    else:
                                        print('接口名称： %s|信息错误：获取用例数据失败|错误信息： %s\n'
                                              % (temp_name_interface, data_case_interface['message']))
                                        print('#####################结束执行接口：%s#################### \n'%temp_name_interface)
                            else:
                                print('错误信息：待执行接口获取失败|错误信息：%s' % module_execute['message'])
            elif value_input == '1':
                print('你输入的是：1|导出测试用例结果，请注意查看目录：%s' % (config.src_path+'\\report'))
                name_export = base_db.select_one("SELECT value_config from config_total "
                                                 "WHERE `status` =1 AND key_config = 'name_export'") # 获取导出的接口数据元组
                print(name_export)
                if name_export['code'] == '0000' and len(name_export['data']['value_config']) != 0:  #判断查询结果
                    temp_export = eval(name_export['data']['value_config']) #获取查询数据，并将其转化为字典
                    test_analyse_data = AnalyseData()
                    result_export = test_analyse_data.export2excel(temp_export) #导出测试结果
                    print(result_export['message'])
                    print("导出失败接口列表: %s\n" % result_export['data'])
                else:
                    print('请检查配置表数据正确性,当前值为：%s \n'%name_export['data'])
    except Exception as e:
        print('系统出现异常：%s ' % e)
        MyLog.error(e)

    input('Press Enter to exit...')




