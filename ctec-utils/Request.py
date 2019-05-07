# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import json
import datetime
import traceback
import uuid

import requests
from requests.adapters import HTTPAdapter
from Models import JournalLog, get_host_ip

APP_NAME = "python3 project"
IP = get_host_ip()


def get(url, params: dict = None, header: dict = None, log=None, timeout: int =5, transaction_id: str="") -> (int, str):
    """
    兼容http请求和https工具
    :param url: 请求地址
    :param params: url参数
    :param header: 头信息
    :param log: 日志对象
    :param timeout: 超时时间
    :param transaction_id: 流水号， 没有则会自动创建
    :return: 返回元组，0是请求成功 响应体，1是请求异常 异常描述
    """
    code, response = 0, ""
    if log:
        log.debug("start url={}, params={}".format(url, params))
    if not transaction_id:
        transaction_id = str(uuid.uuid4()).replace("-", "")
    journal_log = JournalLog(req_app_name=APP_NAME, req_time=datetime.datetime.now(), req_content=str(params),
                             req_host=IP, transaction_id=transaction_id)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                             "537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
    if header:
        headers.update(header)
    try:
        request = requests.Session()
        # http请求最多重试3次
        request.mount('http://', HTTPAdapter(max_retries=3))
        # https请求最多重试3次
        request.mount('https://', HTTPAdapter(max_retries=3))
        response = request.get(url=url, params=params, headers=headers, timeout=timeout)
    except Exception as e:
        code, response = 1, "接口调用异常url={}, params={}, 异常信息={}".format(url, params, traceback.format_exc())
    else:
        try:
            response = response.json()
        except ValueError:
            response = response.content
    finally:
        journal_log.res_time = datetime.datetime.now()
        journal_log.elapse_time = (journal_log.res_time - journal_log.req_time).total_seconds()
        journal_log.req_time = journal_log.req_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        journal_log.res_time = journal_log.res_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        if log:
            log.debug("end response={}".format(response))
            if getattr(log, "external_log"):
                journal_log.res_content = response
                log.external_log(journal_log)

        return code, response


def post(url, data=None, params: dict = None, header: dict = None, log=None, timeout: int = 5,
         transaction_id: str = "") -> (int, str):
    """
    兼容http请求和https工具
    :param url: 请求地址
    :param data: 请求体数据
    :param params: url参数
    :param header: 头信息
    :param log: 日志对象
    :param timeout: 超时时间
    :param transaction_id: 流水号， 没有则会自动创建
    :return: 返回元组，0是请求成功 响应体，1是请求异常 异常描述
    """
    data = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    code, response = 0, ""
    if log:
        log.debug("start url={}, data={}, params={}".format(url, data, params))
    if not transaction_id:
        transaction_id = str(uuid.uuid4()).replace("-", "")
    journal_log = JournalLog(req_app_name=APP_NAME, req_time=datetime.datetime.now(), req_content=data,
                             req_host=IP, transaction_id=transaction_id)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                             "537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
    if header:
        headers.update(header)
    try:
        request = requests.Session()
        # http请求最多重试3次
        request.mount('http://', HTTPAdapter(max_retries=3))
        # https请求最多重试3次
        request.mount('https://', HTTPAdapter(max_retries=3))
        response = request.post(url=url, data=data, params=params, headers=headers, timeout=timeout)
    except Exception as e:
        code, response = 1, "接口调用异常url={}, data={}, params={}, 异常信息={}".format(url, data,
                                                                               params, traceback.format_exc())
    else:
        try:
            response = response.json()
        except ValueError:
            response = response.content
    finally:
        journal_log.res_time = datetime.datetime.now()
        journal_log.elapse_time = (journal_log.res_time - journal_log.req_time).total_seconds()
        journal_log.req_time = journal_log.req_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        journal_log.res_time = journal_log.res_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        if log:
            log.debug("end response={}".format(response))
            if getattr(log, "external_log"):
                journal_log.res_content = response
                log.external_log(journal_log)
        return code, response
