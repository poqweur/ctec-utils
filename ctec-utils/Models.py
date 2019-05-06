# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import time
import os
import socket


MACHINE_NAME = os.environ.get("HOSTNAME", "") + os.environ.get("hostname", "")


class JournalLog:
    """
    新流水日志
    """
    def __init__(self, req_app_name: str = "",
                 res_app_name: str = "",
                 req_time="",
                 res_time="",
                 elapse_time="",
                 req_content: str = "",
                 res_content: str = "",
                 req_host: str = "",
                 res_host: str = "",
                 code: str = "",
                 err_desc: str = "",
                 transaction_id: str = "",
                 request_id: str = ""):
        self.req_app_name: str = req_app_name
        self.res_app_name: str = res_app_name
        self.req_time = req_time
        self.res_time = res_time
        self.elapse_time = elapse_time
        self.req_content: str = req_content
        self.res_content: str = res_content
        self.req_host: str = req_host
        self.res_host: str = res_host
        self.code: str = code
        self.err_desc: str = err_desc
        self.transaction_id: str = transaction_id
        self.request_id: str = request_id


class InternalLog:
    """
    (旧)内部流水模型
    """

    def __init__(self):
        self.id: str = "1"
        self.call_time: time = ""
        self.call_ip: str = ""
        self.call_rev: str = ""
        self.xml_contents: str = ""
        self.response_result: str = ""
        self.response_content: str = ""
        self.response_time: str = ""
        self.transaction_id: str = ""
        self.action_code: str = ""
        self.bus_code: str = ""
        self.service_contractor: str = ""
        self.service_level: str = ""
        self.src_org_id: str = ""
        self.src_sys_id: str = ""
        self.src_sys_sign: str = ""
        self.dst_org_id: str = ""
        self.dstsysid: str = ""
        self.reqtime: time = ""
        self.createdateppm: str = ""
        self.disable_opid: str = ""
        self.disable_date: str = ""
        self.create_opid: str = ""
        self.create_date: str = ""
        self.rec_status: int = 0
        self.flow: int = 0
        self.order_id: str = ""
        self.machinename: str = MACHINE_NAME
        self.feedback_code: str = ""
        self.feedback_content: str = ""


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    # 获取本机计算机名称
    hostname = socket.gethostname()
    # 获取本机ip
    ip = socket.gethostbyname(hostname)
    if ip:
        return ip

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.connect(('8.8.8.8', 80))
        ip = client.getsockname()[0]
    except Exception as e:
        print(e)
        return "未获取到IP"
    else:
        client.close()
    return ip
