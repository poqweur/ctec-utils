# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import json
import datetime
import traceback
import uuid

import requests
from requests.adapters import HTTPAdapter
from Models import InsideOutside


def get(url, params: dict = None, header: dict = None, log=None, timeout: int =5, transaction_id: str="",
        is_external: bool = True) -> (int, str):
    """
    兼容http请求和https工具
    :param url: 请求地址
    :param params: url参数
    :param header: 头信息
    :param log: 日志对象
    :param timeout: 超时时间
    :param transaction_id: 流水号， 没有则会自动创建
    :param is_external: 是否记录外部流水
    :return: 返回元组，0是请求成功 响应体，1是请求异常 异常描述
    """
    code, response = 0, ""
    if log:
        log.debug("start url={}, params={}".format(url, params))
    if not transaction_id:
        transaction_id = str(uuid.uuid4()).replace("-", "")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                             "537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
    if header:
        headers.update(header)
    journal_log = InsideOutside(transaction_id=transaction_id, dialog_type="out", address=url, http_method="GET",
                                key_param=str(params), request_payload=str(params), request_headers=headers)
    journal_log.request_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
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
        journal_log.response_headers = str(response.headers)
        journal_log.response_code = response.status_code
        try:
            response = response.json()
        except ValueError:
            response = response.content
    finally:
        journal_log.response_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        journal_log.response_payload = str(response)

        if log:
            log.debug("end url_params= {}, response={}".format(params, response))
            if is_external and getattr(log, "external_log"):
                journal_log.res_content = response
                log.external(extra=journal_log.__dict__)

        return code, response


def post(url, data=None, params: dict = None, header: dict = None, log=None, timeout: int = 5,
         transaction_id: str = "", is_external: bool = True) -> (int, str):
    """
    兼容http请求和https工具
    :param url: 请求地址
    :param data: 请求体数据
    :param params: url参数
    :param header: 头信息
    :param log: 日志对象
    :param timeout: 超时时间
    :param transaction_id: 流水号， 没有则会自动创建
    :param is_external: 是否记录外部流水
    :return: 返回元组，0是请求成功 响应体，1是请求异常 异常描述
    """
    data = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    code, response = 0, ""
    if log:
        log.debug("start url={}, data={}, params={}".format(url, data, params))
    if not transaction_id:
        transaction_id = str(uuid.uuid4()).replace("-", "")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                             "537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
    if header:
        headers.update(header)

    journal_log = InsideOutside(transaction_id=transaction_id, dialog_type="out", address=url, http_method="POST",
                                key_param=str(data), request_payload=str(data), request_headers=headers)
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
        journal_log.response_code = response.status_code
        journal_log.response_headers = response.headers
        try:
            response = response.json()
        except ValueError:
            response = response.content
    finally:
        journal_log.response_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        journal_log.response_payload = str(response)
        if log:
            log.debug("end data= {}, response={}".format(data, response))
            if is_external and getattr(log, "external_log"):
                journal_log.res_content = response
                log.external(extra=journal_log.__dict__)
        return code, response
