# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import requests


def get(url, params=None, header=None, log=None):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
    if header:
        headers.update(header)
    try:
        response = requests.get(url=url, params=params, headers=headers)
    except Exception as e:
        if log:
            log.error("url={}, data={}, errmsg={}".format(url, params, e))
    else:
        resp = response.content
        if log and getattr(log, "external_log"):
            log.external_log("url={}, data={}, result={}".format(url, params, resp))
        return response.content


def post(url, data=None, params=None, header=None, log=None):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
    if header:
        headers.update(header)
    try:
        response = requests.post(url=url, data=data, params=params, headers=headers)
    except Exception as e:
        if log:
            log.error("url={}, data={}, errmsg={}".format(url, data, e))
    else:
        resp = response.content
        if log and getattr(log, "external_log"):
            log.external_log("url={}, data={}, result={}".format(url, data, resp))
        return resp
