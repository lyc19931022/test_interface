import xlrd
from common.Log import MyLog


class ReadFromExcel(object):
    def __init__(self, path):
        try:
            self.xl = xlrd.open_workbook(path.replace('\\', '/'))
            self.sheet_list = self.xl.sheet_names()
        except Exception as e:
            print(e)

    def readsheet(self, sheet_name):
        """

        :param table_name: sheet表名,若table_name == None,则读取所有table中的数据
        :return: 返回list[
        {'id': 1.0, 'tags': '位置信息', 'name': '获取ip信息接口测试用例-1', 'method': 'get', 'url': 'http://ip.taobao.com/service/getIpInfo.php', 'headers': "{'Host':'ip.taobao.com'}", 'body': "{'ip':'63.223.108.4'}", 'type': 'json', 'return_status_code': '', 'return_text': ''},
        {'id': 2.0, 'tags': '位置信息', 'name': '获取ip信息接口测试用例-2', 'method': 'get', 'url': 'http://ip.taobao.com/service/getIpInfo.php', 'headers': "{'Host':'ip.taobao.com'}", 'body': "{'ip':'127.0.0.1'}", 'type': 'json', 'return_status_code': '', 'return_text': ''}
        ]
        """
        interfaces_list = []
        try:
            if sheet_name is not None:
                sheet = self.xl.sheet_by_name(sheet_name)
            # 获取总列数
            rows = sheet.nrows
            if rows >= 2:
                # 获取第一行数据，作为字典Key值
                keys_list = sheet.row_values(0)

                for i in range(rows):
                    if i >= 1:
                        parmDict = dict(zip(keys_list, sheet.row_values(i)))
                        interfaces_list.append(parmDict)
                        result = {'code': '0000', 'message': '执行批量excel查询表%s操作成功' % sheet_name, 'data': interfaces_list}
                return result
            else:
                print('表名为%s数据为空！' % sheet_name)
                result = {'code': '0000', 'message': '执行批量excel查询操作失败,表名为%s数据为空' % sheet_name, 'data': []}
                return result
        except xlrd.biffh.XLRDError as e:
            print('没有名称为%s的sheet' % sheet_name)
            MyLog.error('没有名称为%s的sheet' % sheet_name)
            result = {'code': '9999', 'message': '执行批量excel查询操作失败,没有名称为%s的sheet' % sheet_name, 'data': []}
            return result

    def readall(self):
        """
        读取excel中所有sheet中的测试用例
        :return:
        """
        interfaces_list = []
        sheets_list = self.xl.sheet_names()
        print(sheets_list)
        if len(sheets_list) != 0:
            for sheet_name in sheets_list:
                sheet = self.xl.sheet_by_name(sheet_name)
                rows = sheet.nrows
                if rows >= 2:
                    # 获取第一行数据，作为字典Key值
                    keys_list = sheet.row_values(0)
                    for i in range(rows):
                        if i >= 1:
                            parmDict = dict(zip(keys_list, sheet.row_values(i)))
                            interfaces_list.append(parmDict)
                else:
                    print('表名为%s数据为空！' % sheet_name)
        return interfaces_list

        # else:
        # print('表名为%s数据为空！' % sheet_name)
        # result = {'code': '0000', 'message': '执行批量excel查询操作失败,表名为%s数据为空' % sheet_name, 'data': []}
        # return result
        # except xlrd.biffh.XLRDError as e:
        # print('没有名称为%s的sheet' % sheet_name)
        # MyLog.error('没有名称为%s的sheet' % sheet_name)
        # result = {'code': '9999', 'message': '执行批量excel查询操作失败,没有名称为%s的sheet' % sheet_name, 'data': []}
        # return result


if __name__ == '__main__':
    obj = ReadFromExcel(r'C:\Users\li\PycharmProjects\test_interface\Testcase\API_TestCases.xlsx')

    r = obj.readall()
    print(r)
    # for i in r:
    #     for k, v in i.items():
    #         print(k, v)
    # print(r)
