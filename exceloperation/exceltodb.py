from common.opmysql import OperationDbInterface
from exceloperation.readfromexcel import ReadFromExcel


class ExcelToDB(object):
    def __init__(self):
        self.db = OperationDbInterface()
        self.table_name = ''

    def setExcelpath(self, file_path):
        self.filepath = file_path

    def intoMysql(self, list=[]):
        excel_op = ReadFromExcel(self.filepath)
        datas_list = excel_op.readall()
        params_list = []
        for data in datas_list:
            name_interface = data.get('name_interface')
            name_case = data.get('name_case')
            exe_mode = data.get('exe_mode')
            url_interface = data.get('url_interface')
            header_interface = data.get('header_interface')
            params_interface = data.get('params_interface')
            check_level = data.get('check_level')
            extra = data.get('extra')
            code_to_compare = data.get('code_to_compare')
            code_expect = data.get('code_expect')
            params_to_compare = data.get('params_to_compare')
            param = (name_interface,
                     name_case,
                     exe_mode,
                     url_interface,
                     header_interface,
                     params_interface,
                     check_level,
                     extra,
                     code_to_compare,
                     code_expect,
                     params_to_compare)
            condition = "INSERT INTO case_interface (" \
                        "name_interface," \
                        "name_case," \
                        "exe_mode," \
                        "url_interface," \
                        "header_interface," \
                        "params_interface," \
                        "check_level," \
                        "extra," \
                        "code_to_compare," \
                        "code_expect," \
                        "params_to_compare)" \
                        "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            params_list.append(param)
        return self.db.insert_data(condition=condition, params=params_list)


if __name__ == '__main__':
    obj = ExcelToDB()
    obj.setExcelpath(file_path=r"C:\Users\li\PycharmProjects\test_interface\Testcase\API_TestCases.xlsx")
    print(obj.intoMysql())
