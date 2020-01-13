# coding=utf8
# __author__ = 'lyc'

import pymysql
from common.Log import MyLog


class OperationDbInterface(object):
    def __init__(self, host_db='127.0.0.1', user_db='root', pwd_db='123456', name_db='test_interface', port_db=3306, link_type=0):
        """
        初始化数据库链接
        :param host_db: 数据库服务主机
        :param user_db: 数据库用户名
        :param pwd_db:  数据库密码
        :param name_db: 数据库名称
        :param port_db: 端口号，整型数据
        :param link_type: 连接类型，用户设置输出数据是元组还是字典，默认是字典，link_type = 0
        :return:游标
        """
        try:
            if link_type == 0:
                self.conn = pymysql.connect(host=host_db,
                                            user=user_db,
                                            password=pwd_db,
                                            db=name_db,
                                            port=port_db,
                                            charset='utf8',
                                            cursorclass=pymysql.cursors.DictCursor)  # 创建数据库连接，返回字典
            else:
                self.conn = pymysql.connect(host=host_db,
                                            user=user_db,
                                            password=pwd_db,
                                            db=name_db,
                                            port=port_db,
                                            charset='utf8')  # 创建数据库连接，返回元组

            self.cur = self.conn.cursor()
        except pymysql.Error as e:
            print("创建数据库连接失败| Mysql Error %d: %s" % (e.args[0], e.args[1]))
            MyLog.error("创建数据库连接失败| Mysql Error %d: %s" % (e.args[0], e.args[1]))

    def op_sql(self, condition):
        """
        定义单条数据库操作，包含删除，更新操作
        :param condition: SQL语句，该通用方法可用来代替updateone, deleteone
        :return: 字典形式
        """
        try:
            self.cur.execute(condition)  # 执行SQL语句
            self.conn.commit()  # 提交游标数据
            result = {'code': '0000', 'message': '执行通用操作成功', 'data': []}
        except pymysql.Error as e:
            self.conn.rollback()  # 执行回滚操作
            result = {'code': '9999', 'message': '执行通用操作异常', 'data': []}

            print("数据库错误| Mysql Error %d: %s" % (e.args[0], e.args[1]))

            MyLog.error(e)
        return result

    def select_one(self, condition):
        """
        查询表中单条数据
        :param condition: SQL语句
        :return: 字典形式的单条查询结果
        """
        try:
            rows_affect = self.cur.execute(condition)

            if rows_affect > 0:  # 查询结果返回数据大于0
                results = self.cur.fetchone()  # 获取一条数据
                result = {'code': '0000', 'message': '执行单条查询操作成功', 'data': results}
            else:
                result = {'code': '0000', 'message': '执行单条查询操作成功', 'data': []}
        except pymysql.Error as e:
            result = {'code': '9999', 'message': '执行单条查询异常', 'data': []}
            print("数据库错误| Mysql Error %d: %s" % (e.args[0], e.args[1]))
            MyLog.error("数据库错误| Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return result

    def select_all(self, condition):
        """
        查询表中多条数据
        :param condition: SQL语句
        :return: 字典形式的批量查询结果
        """
        try:
            rows_affect = self.cur.execute(condition)
            if rows_affect > 0:  # 查询结果返回数据大于0
                self.cur.scroll(0, mode='absolute')  # 将鼠标光标放回到初始位置
                results = self.cur.fetchall()  # 返回游标中所有结果
                result = {'code': '0000', 'message': '执行批量查询操作成功', 'data': results}
            else:
                result = {'code': '0000', 'message': '执行批量查询操作成功', 'data': []}
        except pymysql.Error as e:
            result = {'code': '9999', 'message': '执行批量查询异常', 'data': []}
            print("数据库错误| Mysql Error %d: %s" % (e.args[0], e.args[1]))
            MyLog.error("数据库错误| Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return result

    def insert_data(self, condition, params):
        """
        定义表中插入操作
        :param condition: insert 语句
        :param params:数据，列表形式[('3','Tom','1 year 1 class','6'),('3','Jack','2 year 1 class','7')]
        :return:字典形式的批量插入数据结果
        """
        try:
            results = self.cur.executemany(condition, params)  # 返回插入的数据条数
            self.conn.commit()
            result = {'code': '0000', 'message': '执行批量插入操作成功', 'data': results}
        except pymysql.Error as e:
            self.conn.rollback()  # 执行回滚操作
            result = {'code': '9999', 'message': '执行批量插入操作异常', 'data': []}
            print("数据库错误| Mysql Error %d: %s" % (e.args[0], e.args[1]))
            MyLog.error("数据库错误| Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return result

    def __del__(self):
        """
        关闭数据库
        :return:
        """
        if self.cur is not None:
            self.cur.close()  # 关闭游标
        if self.conn is not None:
            self.conn.close()  # 释放数据库资源


if __name__ == '__main__':
    obj = OperationDbInterface(link_type=1)
    sql = "INSERT INTO config_total (key_config,value_config,description,`status`) VALUES(%s,%s,%s,%s)"
    print(obj.insert_data("INSERT INTO config_total (key_config,value_config,description,`status`) VALUES(%s,%s,%s,%s)",
                          [('hahaha','lalalal','测试',0),('121212','lalalal','测试',0)]))
