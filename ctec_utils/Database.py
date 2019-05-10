# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import traceback

import cx_Oracle
import pymysql
from DBUtils.PooledDB import PooledDB
from rediscluster import StrictRedisCluster
from pymongo import MongoClient


class OraclePool(object):
    """
    封装cx_oracle，创建连接池对象

    示例：
        oracle = OraclePool(用户名, 密码, 'ip/库' 或 dsn, 最小连接数, 最大连接数)
    """

    def __init__(self, user: str, password: str, dsn: str, mincached: int, maxcached: int, threaded: bool = False,
                 log=None):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.min_cached = mincached
        self.max_cached = maxcached
        self.threaded = threaded
        self.log = log
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

    def procedure_cursor(self, procedure_name: str, *args, commit: bool = False):
        """
        存储过程返回游标对象
        :param procedure_name: 存过名
        :param args: 入参
        :param commit: 是否commit
        :return:
        """
        conn = None
        return_list = []
        try:
            conn = self.__connection.connection()
            cursor = conn.cursor()
            result = cursor.var(cx_Oracle.CURSOR)
            params = list(args)
            params.append(result)
            _, resp_result = cursor.callproc(procedure_name, params)
            if commit:
                conn.commit()
            conn.close()
        except Exception as e:
            if conn:
                self.rollback(conn)
            if self.log:
                self.log.error("{}, params={}, errmsg={}".format(procedure_name, args, traceback.format_exc()))
            return None
        else:
            for res in list(result.getvalue()):
                return_list.append(dict(zip([resp[0] for resp in resp_result.description], res)))
            if self.log:
                self.log.debug("{}, params={}, result={}".format(procedure_name, args, return_list))
            return return_list

    def procedure_string(self, procedure_name: str, *args, commit: bool = False):
        """
        存储过程返回值
        :param procedure_name: 存过名
        :param args: 入参
        :param commit: 是否commit
        :return:
        """
        conn = None
        try:
            conn = self.__connection.connection()
            cursor = conn.cursor()
            result = cursor.var(cx_Oracle.STRING)
            params = list(args)
            params.append(result)
            cursor.callproc(procedure_name, params)
            if commit:
                conn.commit()
            conn.close()
        except Exception as e:
            if conn:
                self.rollback(conn)
            if self.log:
                self.log.error("{}, params={}, errmsg={}".format(procedure_name, args, traceback.format_exc()))
            return None
        else:
            if self.log:
                self.log.debug("{}, params={}, result={}".format(procedure_name, args, result))
            return result.getvalue()

    def row_sql(self, sql: str, param: dict, commit: bool = False):
        """
        原生sql

        例如：
            o = OraclePool("user", "password", 'dsn', 0, 1)
            print(o.row_sql("select * from 表 where ROWNUM < :num", {"num": 10}))
        :param sql: sql语句
        :param param: 入参
        :param commit: 是否commit
        :return:
        """
        conn = None
        try:
            conn = self.__connection.connection()
            cursor = conn.cursor()
            return_result = list()
            result_db = cursor.execute(sql, param)
            if commit:
                cursor.commit()
            result = result_db.fetchall()
        except Exception as e:
            if conn:
                self.rollback(conn)
            if self.log:
                self.log.error("{}, params={}, errmsg={}".format(sql, param, traceback.format_exc()))
            return None
        else:
            if self.log:
                self.log.debug("{}, params={}, result={}".format(sql, param, result))

            if isinstance(result, list) and len(result) > 0:
                key_list = [key[0] for key in result_db.description]
                for value in result:
                    return_result.append(dict(zip(key_list, value)))
                return return_result
            return result

    def rollback(self, conn):
        conn.rollback()


class RedisCluster(object):
    """
    连接redis集群

    示例：
        redis_nodes = [
            {'host': '172.16.0.1', 'port': 7001},
            {'host': '172.16.0.2', 'port': 7002},
        ]

        redis = RedisCluster(redis_nodes)
        conn = redis.conn
        conn.get("键")
    """

    def __init__(self, redis_nodes: list):
        self.redis_nodes = redis_nodes
        self.conn = self.get_conn()

    def get_conn(self):
        return StrictRedisCluster(startup_nodes=self.redis_nodes)


class MongodbCluster(object):
    """
    连接mongodb集群

    示例：
        mongodb_nodes = [
             {'host': '172.16.0.1', 'port': 7001},
             {'host': '172.16.0.2', 'port': 7002},
        ]

        mongodb = Mongodb("user", "password", mongodb_nodes)
        mongodb.conn
    """

    def __init__(self, user: str, password: str, hosts: list):
        self.user = user
        self.password = password
        self.conn = self.get_connect(hosts)

    def get_connect(self, hosts):
        hosts_list = ",".join(["{}:{}".format(host["host"], host["port"]) for host in hosts])
        url = "mongodb://{user}:{password}@{list}".format(user=self.user, password=self.password, list=hosts_list)
        return MongoClient(url)


class MysqlPool(object):
    """
    mysql连接池

    示例：

        mysql = MysqlPool(host=host, port=3306, user="root", password="mysql", mincached=0, maxcached=1, db=库名)
        print(mysql.row_sql("show databases;"))
    """
    def __init__(self, user: str, password: str, host: str, port: int, mincached: int, maxcached: int,
                 db: str, log=None):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db = db
        self.min_cached = mincached
        self.max_cached = maxcached
        self.log = log
        self.__connection = self.__get_connect()

    def __get_connect(self):
        # setsession=['SET AUTOCOMMIT = 1']是用来设置线程池是否打开自动更新的配置，0为False，1为True
        return PooledDB(pymysql,
                        host=self.host,
                        user=self.user,
                        passwd=self.password,
                        db=self.db,
                        port=self.port,
                        mincached=self.min_cached,
                        maxcached=self.max_cached)

    def row_sql(self, sql, param=None, commit=False):
        """
        暂时只提供原生sql
        :param sql: sql语句
        :param param: 参数
        :param commit: 是否commit
        :return:
        """
        conn = None
        try:
            conn = self.__connection.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(sql, param)
            results = cur.fetchall()
            if commit:
                cur.commit()
            conn.close()
        except Exception as e:
            if conn:
                self.rollback(conn)
            if self.log:
                self.log.error("{}, param={}, errmsg={}".format(sql, param, traceback.format_exc()))
            return None
        else:
            if self.log:
                self.log.debug("{}, param={}, success={}".format(sql, param, results))
            return results

    def rollback(self, conn):
        conn.rollback()

