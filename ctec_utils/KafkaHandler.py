# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy

import logging
import logging.config

from kafka.client import KafkaClient, SimpleClient
from kafka.producer import SimpleProducer, KeyedProducer
from logstash_formatter import LogstashFormatterV1, LogstashFormatter

MODEL = {
    0: LogstashFormatterV1,
    1: LogstashFormatter
}


class KafkaLoggingHandler(logging.Handler):

    def __init__(self, hosts_list: str or list, topic: str, timeout_secs: int = 120, model: int = 0, **kwargs):
        self.hosts_list = hosts_list
        self.topic = topic
        self.timeout_secs = timeout_secs
        self.model = model
        self.kwargs = kwargs

        logging.Handler.__init__(self)
        self.formatter = MODEL[model]()

        self.key = kwargs.get("key", None)
        try:
            self.kafka_client = KafkaClient(bootstrap_servers=hosts_list, timeout=timeout_secs) if self.key \
                else SimpleClient(hosts=hosts_list, timeout=timeout_secs)
        except Exception as e:
            raise e
        self.kafka_topic_name = topic

        if not self.key:
            self.producer = SimpleProducer(self.kafka_client, **kwargs)
        else:
            self.producer = KeyedProducer(self.kafka_client, **kwargs)

    def emit(self, record, flag=3):
        if flag > 0:
            # drop kafka logging to avoid infinite recursion
            if record.name == 'kafka':
                return
            try:
                # use default formatting
                msg = self.format(record)
                if isinstance(msg, str):
                    msg = msg.encode("utf-8")

                # produce message
                if not self.key:
                    self.producer.send_messages(self.kafka_topic_name, msg)
                else:
                    self.producer.send_messages(self.kafka_topic_name, self.key, msg)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.__init__(self.hosts_list, self.topic, self.timeout_secs, self.model, **self.kwargs)
                # self.handleError(record)
        else:
            self.handleError(record)

    def close(self):
        if self.producer is not None:
            self.producer.stop()
        logging.Handler.close(self)


class ThirdLog(logging.Logger):

    def __init__(self, name: str, hostname: str, logger_name: str):
        """
        参数描述
        :param name: 日志对象名
        :param hostname: 主机名
        :param logger_name: 日志类名
        """
        super().__init__(name)
        self.hostname = hostname
        self.logger_name = logger_name

    def params(self):
        """
        组建格式
        :return:
        """
        extra = {
            "app_name": self.name,
            "logger": self.logger_name,
            "HOSTNAME": self.hostname}
        return extra

    def debug(self, msg: str, *args, log_type="desc", **kwargs):
        """
        :param msg: 描述
        :param args:
        :param log_type: /desc/monitor/visit 等
        :param kwargs:
        :return:
        """
        extra = self.params()
        extra.update({"level": "DEBUG", "log_type": log_type})
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, extra=extra, **kwargs)

    def info(self, msg: str, *args, log_type="desc", **kwargs):
        """
        :param msg: 描述
        :param args:
        :param log_type: /desc/monitor/visit 等
        :param kwargs:
        :return:
        """
        extra = self.params()
        extra.update({"level": "INFO", "log_type": log_type})
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, extra=extra, **kwargs)

    def error(self, msg: str, *args, log_type="desc", **kwargs):
        """
        :param msg: 描述
        :param args:
        :param log_type: /desc/monitor/visit 等
        :param kwargs:
        :return:
        """
        extra = self.params()
        extra.update({"level": "ERROR", "log_type": log_type})
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, extra=extra, **kwargs)

    def warning(self, msg: str, *args, log_type="desc", **kwargs):
        """
        :param msg: 描述
        :param args:
        :param log_type: /desc/monitor/visit 等
        :param kwargs:
        :return:
        """
        extra = self.params()
        extra.update({"level": "WARNING", "log_type": log_type})
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, extra=extra, **kwargs)

    def external(self, msg: str, *args, log_type="desc", **kwargs):
        """
        :param msg: 描述
        :param args:
        :param log_type: /desc/monitor/visit 等
        :param kwargs:
        :return:
        """
        extra = self.params()
        extra.update({"level": "INFO", "log_type": log_type})
        ex = kwargs.get("extra")
        if ex:
            extra.update(ex)
            del kwargs["extra"]
        self._log(logging.INFO, msg, args, extra=extra, **kwargs)

    def internal(self, msg: str, *args, log_type="desc", **kwargs):
        """
        :param msg: 描述
        :param args:
        :param log_type: /desc/monitor/visit 等
        :param kwargs:
        :return:
        """
        extra = self.params()
        extra.update({"level": "INFO", "log_type": log_type})
        ex = kwargs.get("extra")
        if ex:
            extra.update(ex)
            del kwargs["extra"]
        self._log(logging.INFO, msg, args, extra=extra, **kwargs)
