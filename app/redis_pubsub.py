import redis

# 发布订阅模式的发布者
class Publisher:
    
    def __init__(self, host='localhost', id=0, name='default'):
        '''
        : __init__: 初始化发布者
        : param host: redis数据库连接主机，成对的发布者和订阅者初始化的时候应当使用相同的连接主机
        : type host: str
        : param id: redis数据库创建编号，默认值为redis的默认值0，成对的发布者和订阅者初始化的时候应当使用相同的编号
        : type id: int
        : param name: redis的订阅通道指定名称，订阅通道名称将作为redis数据库中存储的键值对的左值，成对的发布者和订阅者初始化的时候应当使用相同的订阅通道名称
        : type name: str
        '''
        self.host = host
        self.id = id
        self.name = name                                      # 指定订阅通道名称

        self.db = redis.StrictRedis(host=host, db=id)         # 创建数据库
        self.tube = self.db.pubsub()        # 发布和订阅过程所使用的通道
        self.tube.subscribe(self.name)      # 将通道和通道名称绑定

    def getinfo(self):
        '''
        : getinfo: 获取该类的对象的数据库连接信息
        : return: 数据库连接信息三元组(host, db, name)
        : rtype: tuple(str, str, str)
        '''
        return (self.host, self.db, self.name)

    def publish(self, content):
        '''
        : produce: 生产者生产消息
        : param content: 要生产的信息，在本项目中为任务id，作为redis数据库存储的键值对的右值
        : type content: int
        : return: 生产的信息，返回值和参数content相等
        : rtype: int
        '''
        self.db.publish(self.name, content)     # 发布者发布消息

        return content


    
# 发布订阅模式的订阅者
class Subscriber:
    
    def __init__(self, host='localhost', id=0, name='default'):
        '''
        : __init__: 初始化订阅者
        : param host: redis数据库连接主机，成对的发布者和订阅者初始化的时候应当使用相同的连接主机
        : type host: str
        : param id: redis数据库创建编号，默认值为redis的默认值0，成对的发布者和订阅者初始化的时候应当使用相同的编号
        : type id: int
        : param name: redis的订阅通道指定名称，订阅通道名称将作为redis数据库中存储的键值对的左值，成对的发布者和订阅者初始化的时候应当使用相同的订阅通道名称
        : type name: str
        '''
        self.host = host
        self.id = id
        self.name = name                                      # 指定订阅通道名称

        self.db = redis.StrictRedis(host=host, db=id)         # 创建数据库
        self.tube = self.db.pubsub()        # 发布和订阅过程所使用的通道
        self.tube.subscribe(self.name)      # 将通道和通道名称绑定

    def getinfo(self):
        '''
        : getinfo: 获取该类的对象的数据库连接信息
        : return: 数据库连接信息三元组(host, db, name)
        : rtype: tuple(str, str, str)
        '''
        return (self.host, self.db, self.name)

    def subscribe(self):
        '''
        : subscribe: 订阅者订阅接受一个消息
        : param content: 要接受的订阅信息，在本项目中为任务id，作为redis数据库存储的键值对的右值
        : type content: int
        : return: 收到的信息
        : rtype: int
        '''
        for content in self.tube.listen():
            if content['type'] == 'message':
                print(content['data'])
        
        return content

    
