# coding=utf8
import datetime
from xlrd import open_workbook
from xlutils.copy import copy
from public import config
from common.opmysql import OperationDbInterface
from common.Log import MyLog


class AnalyseData(object):
    """
    定义对接口测试数据进行分析的类，包含的方法有:
    1.导出测试数据到Excel中
    """

    def __init__(self):
        self.field = config.filed_excel  # 初始化配置文件
        self.db = OperationDbInterface(link_type=1)  # 初始化数据库操作类，返回元组

    def export2excel(self, name_export):
        """

        :param name_export: 待导出的接口名称，列表形式
        :return:
        """
        counts_export = len(name_export)  # 导出总数
        fail_export = []  # 导出失败接口列表
        try:
            src = open_workbook(config.src_path + '/report/report_module.xls', formatting_info=True)
            destination = copy(src)
            dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 当前的时间戳
            filepath = config.src_path + '/report/' + str(dt) + '.xls'
            destination.save(filepath)  # 保存模板表格到新的目录下
            for name_interface in name_export:
                cases_interface = self.db.select_all("SELECT * FROM case_interface "
                                                     "WHERE case_status = 1 "
                                                     "and name_interface = '%s'" % name_interface)

                if len(cases_interface.get('data')) != 0 and cases_interface.get('code') == '0000':
                    src = open_workbook(filepath, formatting_info=True)
                    destination = copy(src)
                    sheet = destination.add_sheet(name_interface, cell_overwrite_ok=True)
                    for col in range(0, len(self.field)):
                        sheet.write(0, col, self.field[col])  # 获取并写入数据段信息到Sheet中
                    for row in range(1, len(cases_interface['data']) + 1):
                        for col in range(0, len(self.field)):
                            sheet.write(row, col, '%s' % cases_interface['data'][row - 1][col])  # 写数据到对应Excel表中

                    destination.save(filepath)
                elif len(cases_interface['data']) == 0 and cases_interface['code'] == '0000':
                    fail_export.append(name_interface)
                else:
                    fail_export.append(name_interface)
            result = {'code': '0000', 'message': '导出总数: %s , 失败数: %s' % (counts_export, len(fail_export)),
                      'data': fail_export}

        except Exception as e:
            MyLog.error(e)
            result = {'code': '9999', 'message': '导出过程异常|导出总数: %s , 失败数: %s' % (counts_export, len(fail_export)),
                      'data': fail_export}
        finally:
            return result


if __name__ == '__main__':
    names_export = OperationDbInterface(link_type=1).select_one("SELECT value_config from config_total WHERE `status` =1 AND key_config = 'name_export'")
    if names_export['code'] =='0000':
        temp_export = eval(names_export['data'][0])
    s = AnalyseData().export2excel(temp_export)
    print(s)

