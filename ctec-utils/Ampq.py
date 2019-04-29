# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import json
import pika


class AsyncPublish:
    """
    未测试异步发送队列
    """

    def __init__(self, host, port, user, password, vhost):
        credentials = pika.PlainCredentials(user, password)
        self.parameters = pika.ConnectionParameters(host, port, vhost,
                                                    credentials)
        self.connection = None
        self.channel = None
        self.exchange = None
        self.data = ""
        self.routing_key = ""

    def get_connection(self):
        return pika.SelectConnection(parameters=self.parameters,
                                     on_open_callback=self.on_open)

    def on_open(self, connection):
        connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=self.routing_key,
                                   body=self.data,
                                   properties=pika.BasicProperties(content_type='text/plain',
                                                                   delivery_mode=1))
        self.connection.close()

    def stop(self):
        try:
            self.channel.close()
            self.connection.close()
        except Exception as e:
            return e

    def send(self, data, exchange, routing_key=""):
        try:
            self.data = data if isinstance(data, str) else json.dumps(data)
            self.exchange = exchange
            self.routing_key = routing_key
            self.connection = self.get_connection()
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.stop()
            if (self.connection is not None and
                    not self.connection.is_closed):
                # Finish closing
                self.connection.ioloop.start()


class Publish:

    def __init__(self, host, port, user, password, vhost, log=None):
        self.params = {"host": host, "port": port, "user": user,
                       "password": password, "vhost": vhost}
        self.log = log
        self.connection = self.get_connection()
        self.channel = self.connection.channel()

    def get_connection(self):
        credentials = pika.PlainCredentials(self.params["user"], self.params["password"])
        parameters = pika.ConnectionParameters(self.params["host"], self.params["port"], self.params["vhost"],
                                               credentials)
        return pika.BlockingConnection(parameters=parameters)

    def stop(self):
        try:
            self.channel.close()
            self.connection.close()
        except Exception as e:
            return e

    def send(self, data, exchange, routing_key="", flag=3):
        data = data if isinstance(data, str) else json.dumps(data)
        if flag > 0:
            try:
                self.channel.basic_publish(exchange=exchange,
                                           routing_key=routing_key,
                                           body=data,
                                           properties=pika.spec.BasicProperties(delivery_mode=2))
                if self.log:
                    self.log.debug("发送exchange={},routing_key={}成功,数据：{}".format(exchange, routing_key, data))
            except Exception as e:
                if self.log:
                    self.log.error("发送exchange={},routing_key={}异常,数据：{}".format(exchange, routing_key, data))
                flag -= 1
                self.stop()
                self.connection = self.get_connection()
                self.send(data, exchange, routing_key)
                return e
        else:
            if self.log:
                self.log.debug("发送exchange={}, routing_key={}失败,数据：{}".format(exchange, routing_key, data))


if __name__ == '__main__':
    p = Publish("172.16.20.73", 5672, "smallrabbit", "123456", "order")
    for i in range(10):
        print(i)
        print(p.send('{"ok": %d}' % i, 'wjy.test'))
