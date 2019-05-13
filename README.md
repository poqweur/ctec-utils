### Project description

**Python version must be greater than 3.7.1**

Based on the package

- pika==0.13.1
- requests==2.20.0
- DBUtils==1.3
- cx_Oracle==7.1.1
- redis-py-cluster==1.3.4
- pymongo==3.8.0
- pymysql==0.9.3
- six==1.12.0
- kafka-python==1.4.6
- logstash-formatter==0.5.17


*The sample code*
### Oracle Pool
```python
from cetc_utils import OraclePool

db = OraclePool("e_tyxb_log", "e_tyxb_log", "172.16.50.67/orcl",0, 1)
result = db.procedure_cursor("存储过程", "入参")
print(result)
```
### Redis Crowd
```python
from cetc_utils import RedisCluster

redis_nodes = [
    {"host": "172.16.50.1", "port": 7001},
    {"host": "172.16.50.2", "port": 7002},
]

re = RedisCluster(redis_nodes).get_conn()

for i in range(14900000011, 14900000021):
    # re.set("user_phone_" + str(i), "888888")
    print(re.get("user_phone_" + str(i)))
```
### Mongodb Crowd
```python
from cetc_utils import MongodbCluster

mongodb_nodes = [
    {"host": "172.16.50.1", "port": 7001},
    {"host": "172.16.50.2", "port": 7002},
]

m = MongodbCluster("user", "password", mongodb_nodes)
print(m.conn)
print(m.nodes)
print(m.database_names())
```
### Mysql Pool
```python
from ctec_utils import MysqlPool

m = MysqlPool(host="ip", port=3306, user="root", password="mysql", mincached=0, maxcached=1, db="s3")
print(m.row_sql("show databases;"))
```
### RabbitMq Publish
```python
from ctec_utils import Publish, AsyncPublish

p = AsyncPublish("ip", 5672, "username", "password", "exchange")
for i in range(10):
    print(i)
    print(p.send('{"test": %d}' % i, 'wjy.test'))

---------------------------------------------------------------------------------

p = Publish("ip", 5672, "username", "password", "exchange")
for i in range(10):
    print(i)
    print(p.send('{"test": %d}' % i, 'wjy.test'))
```
### Request
```python
from ctec_utils import Request
# 如果响应是json格式自动转为字典

code, response = Request.get(url, params, log)
print(code, response)

code, response = Request.post(url, data, log)
print(code, response)
```
### Work template
```python
from ctec_utils.Models import InsideOutside, InternalLog, ExternalInterfaceLoggingEvent, OrderJournalEvent, IssueJobJournal
# (新)内外部流水日志模型、(旧)内部流水日志模型、 外部流水日志模型、 订单流水日志模型、 业务层流水日志模型
```
### KafkaLoggingHandler、ThirdLog
```
from ctec_utils.KafkaHandler import KafkaLoggingHandler, ThirdLog


newLog = ThirdLog("ctec-utils", "sd", "ctec-utils")
fh = logging.FileHandler('test.log')
formatter = logging.Formatter("[%(asctime)s] %(levelname)s::(%(process)d %(thread)d)::%(module)s(%(funcName)s:%(lineno)d): %(message)s")
fh.setFormatter(formatter)
newLog.setLevel(logging.DEBUG)
newLog.addHandler(fh)
newLog.addHandler(KafkaLoggingHandler("ip:port", "super_topic_test",))

newLog.info('logger info message')
newLog.warning('logger warning message')
newLog.error('logger error message')
newLog.critical('logger critical message')

```


打包命令

    python3 setup.py sdist
    python3 setup.py sdist upload
    python3 setup.py bdist_wheel --universal
    python3 setup.py bdist_wheel upload
