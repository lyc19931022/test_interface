import re
from common.opmysql import OperationDbInterface
from common.request import RequestInterface




if __name__ == '__main__':
    data_list = []
    base_request = RequestInterface()
    base_db = OperationDbInterface()

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

                for one_data in data_case_interface.get('data'):
                    data_list.append((one_data.get('name_interface'),one_data))

    print(data_list)


