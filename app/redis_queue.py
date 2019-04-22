import redis

# 使用redis非关系型数据库实现的消息队列

# redis实现消息队列总共有两种实现方法，一是生产消费模式，二是发布订阅模式，下面给出两种redis消息队列的典型实现

# 生产消费者模式的生产者
class Producer:
    
    def __init__(self, host='localhost', id=0, name='default'):
        '''
        : __init__: 初始化生产者
        : param host: redis数据库连接主机，成对的消费者和生产者初始化的时候应当使用相同的连接主机
        : type host: str
        : param id: redis数据库创建编号，默认值为redis的默认值0，成对的消费者和生产者初始化的时候应当使用相同的编号
        : type id: int
        : param name: redis的队列指定名称，队列名称将作为redis数据库中存储的键值对的左值，成对的消费者和生产者初始化的时候应当使用相同的队列名称
        : type name: str
        : note: 不推荐使用初始化方法的默认参数，因为随意的使用容易导致不配对的生产者和消费者指向相同的redis数据库
        '''
        self.host = host
        self.id = id
        self.name = name                                      # 指定队列名称

        self.db = redis.StrictRedis(host=host, db=id)         # 创建数据库

    def getinfo(self):
        '''
        : getinfo: 获取该类的对象的数据库连接信息
        : return: 数据库连接信息三元组(host, db, name)
        : rtype: tuple(str, str, str)
        '''
        return (self.host, self.db, self.name)
    
    def produce(self, content):
        '''
        : produce: 生产者生产消息
        : param content: 要生产的信息，在本项目中为任务id，作为redis数据库存储的键值对的右值
        : type content: int
        : return: 生产的信息，返回值和参数content相等
        : rtype: int
        '''
        # 使用redis的rpush方法，从队列右侧入队所生产的消息，rpush的两个参数分别为键和值
        self.db.rpush(self.name, content)

        return int(content)    # 注意redis中储存的是type类型，需要首先类型转换为int类型
    

# 生产消费者模式的消费者
class Consumer:

    def __init__(self, host='localhost', id=0, name='default'):
        '''
        : __init__: 初始化消费者
        : param host: redis数据库连接主机，成对的消费者和生产者初始化的时候应当使用相同的连接主机
        : type host: str
        : param id: redis数据库创建编号，默认值为redis的默认值0，成对的消费者和生产者初始化的时候应当使用相同的编号
        : type id: int
        : param name: redis的队列指定名称，队列名称将作为redis数据库中存储的键值对的左值，成对的消费者和生产者初始化的时候应当使用相同的队列名称
        : type name: str
        : note: 不推荐使用初始化方法的默认参数，因为随意的使用容易导致不配对的生产者和消费者指向相同的redis数据库
        '''
        self.host = host
        self.id = id
        self.name = name                                      # 指定队列名称

        self.db = redis.StrictRedis(host=host, db=id)         # 创建数据库                                  

    def getinfo(self):
        '''
        : getinfo: 获取该类的对象的数据库连接信息
        : return: 数据库连接信息三元组(host, db, name)
        : rtype: tuple(str, str, str)
        '''
        return (self.host, self.db, self.name)
    
    def consume(self):
        '''
        : consume: 消费者消费队列中的一个信息 (实际使用时，该方法应当被循环调用)
        : return: 所消费的单个信息，在本项目中为任务id，即redis数据库存储的键值对的右值
        : rtype: int
        '''
        # 使用redis的blpop方法，从队列左侧出队要消费的单个消息，若队列中无消息则进入阻塞状态，blpop的第一个参数为键，第二个参数为阻塞时限，设为0表示阻塞时间可以无限期延长
        content = self.db.blpop(self.name, 0)[1]
        return int(content)