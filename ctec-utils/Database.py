# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import cx_Oracle
from DBUtils.PooledDB import PooledDB
from rediscluster import StrictRedisCluster


class OraclePool(object):
    """
    封装连接池对象
    """

    def __init__(self, user, password, dsn, mincached, maxcached, threaded=False):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.min_cached = mincached
        self.max_cached = maxcached
        self.threaded = threaded
        self.__connection = self.__get_connect()

    def __get_connect(self):
        # 创建连接对象
        return PooledDB(cx_Oracle,
                        user=self.user,
                        password=self.password,
                        dsn=self.dsn,
                        mincached=self.min_cached,
                        maxcached=self.max_cached,
                        threaded=self.threaded)

    def procedure_cursor(self, procedure_name, *args):
        try:
            conn = self.__connection.connection()
            cursor = conn.cursor()
            result = cursor.var(cx_Oracle.CURSOR)
            params = list(args)
            params.append(result)
            cursor.callproc(procedure_name, params)
            conn.commit()
            conn.close()
        except Exception as e:
            self.close()
            self.__connection = self.__get_connect()
            print(e)
        else:
            return result.getvalue()

    def procedure_string(self, procedure_name, *args):
        try:
            conn = self.__connection.connection()
            cursor = conn.cursor()
            result = cursor.var(cx_Oracle.STRING)
            cursor.callproc(procedure_name, args)
            conn.commit()
            conn.close()
        except Exception as e:
            self.close()
            self.__connection = self.__get_connect()
            return e
        else:
            return result

    def row_sql(self, sql, param):
        try:
            conn = self.__connection.connection()
            cursor = conn.cursor()
            return_result = list()
            result_db = cursor.execute(sql, param)
            result = result_db.fetchall()
        except Exception as e:
            self.close()
            self.__connection = self.__get_connect()
            return e
        else:
            if len(result) > 0:
                key_list = [key[0] for key in result_db.description]
                for value in result:
                    return_result.append(dict(zip(key_list, value)))
            return return_result

    def __del__(self):
        self.close()

    def close(self):
        try:
            self.__connection.close()
        except:
            pass


class RedisCluster(object):

    def __init__(self, redis_nodes):
        self.redis_nodes = redis_nodes

    def get_conn(self):
        return StrictRedisCluster(startup_nodes=self.redis_nodes)



if __name__ == '__main__':
    # db = OraclePool("e_tyxb_log", "e_tyxb_log", '172.16.50.67/orcl',0, 1)
    # result = db.procedure_cursor("SP_QUERY_LOG_ORDER_ISSUE", "83917080900201000396")
    # print(list(result))
    redis_nodes = [
        {'host': '10.128.112.111', 'port': 7001},
        {'host': '10.128.112.111', 'port': 7002},
    ]

    re = RedisCluster(redis_nodes).get_conn()

    for i in range(14900000011, 14900000021):
        re.set('user_phone_' + str(i), '888888')
        print(re.get('user_phone_' + str(i)))
