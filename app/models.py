# 数据库表单

# 警告：本表单不允许任意修改，一旦修改必须先做'迁移数据库+更新数据库'两部分操作，然后才允许继续修改其他程序的部分

from datetime import datetime
import app
from app import db, login
from flask_login import UserMixin
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

enable_search = True

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# 用户账户表User
# 用户账户表表示每一个在任务系统上注册的用户的主要信息
class User(UserMixin, db.Model):

    # 用户的基本信息是需要频繁查询的(登录和全局搜索功能)，因此推荐各个字段使用索引
    id = db.Column(db.Integer, primary_key = True)                               # 用户id，Integer类型，作为表User的主键，唯一确定一个特定的用户
    username = db.Column(db.String(64), index = True, unique = False)            # 用户昵称，String类型
    email = db.Column(db.String(120), index = True, unique = True)               # 用户邮箱，String类型
    password_hash = db.Column(db.String(128))                                    # 用户密码的哈希值，String类型

    description = db.Column(db.String(140))                                      # 该用户的自我介绍和描述，String类型
    sign = db.Column(db.String(20))                                              # 用户个性签名
    job = db.Column(db.String(20))                                               # 用户职业
    location = db.Column(db.String(100))                                         # 该用户的所在地址

    posts = db.relationship('Post', backref='author', lazy='dynamic')            # 该用户所发送的Post，这里使用的是SQLAlchemy的第二类db.relationship方法，该方法在表Post中增加一个属性author，该属性直接返回Post对象所属于的User对象，也即可以直接通过Post表的该属性访问发送这条Post的用户的对象User

    followed = db.relationship('User',                                           # 该用户的关注关系，followers为追随者
        secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', lazy = 'dynamic'),
        lazy = 'dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        '''
        : set_password: 设定用户密码
        : param password: 需要设定的用户原始密码
        : type password: str
        : return: None
        '''
        # 附注：服务器中不保存用户的原始密码，只保存用户原始密码的哈希值（哈希值足够安全，无法从哈希值还原原始密码）
        self.password_hash = generate_password_hash(password)   

    def check_password(self, password):
        '''
        : check_password: 检查输入的密码是否和用户密码一致
        : param password: 用户输入的密码
        : type password: str
        : return: 检查结果，检查正确则为True，检查错误则为False
        : rtype: bool
        '''
        # 附注；服务器收到用户输入的原始密码值，调用check_password_hash方法，该方法首先将输入的密码进行哈希，然后比较输入的密码的哈希值和保存的正确密码的哈希值是否相等
        return check_password_hash(self.password_hash, password)  

    def get_avatar(self, size):
        '''
        : get_avatar: 获取用户头像
        : param size: 需要获取的头像大小
        : type size: int
        : return: 头像url地址
        : rtype: str
        '''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    def follow(self, user):
        '''
        : follow: 关注某个用户
        '''
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        '''
        : unfollow: 取消关注某个用户
        '''
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        '''
        : is_following: 检查是否正在关注某个用户
        : note: 检查是否正在关注某个用户的方法较为简单，就是直接sql查询并计数
        '''
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def followed_posts(self):
        '''
        : followed_posts: 查询
        : notes: 我们在这里将查询步骤设置为3步：第一步是将followers表和Post表相连接，得到每个用户所关注的用户的全部任务，第二步是筛选用户，用户的id应该等同于当前登录的用户id，第三步是进行排序，因为显示任务动态时往往均显示最新的任务动态，因此需要按照时间戳进行排序
        '''
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())
    
    def follow_list(self):
        '''
        : follow_list: 查询当前用户的粉丝列表
        '''
        # 注意这里的两步操作，ORM中的查询语句没有sql语句这么清晰
        # 1. 将User和followers连接，连接条件是User的id和follow关系的关注者id即follower_id相同，以查出每个followed_id的粉丝follower_id的对应账户信息
        # 2. 从上述结果中令followed_id==self.id，筛选出当前用户的粉丝列表
        return User.query.join(followers, (followers.c.follower_id == User.id)).filter(followers.c.followed_id == self.id)
    
    def followed_list(self):
        '''
        : followed_list: 查询当前用户关注的人的列表
        '''
        # 这里的两步搜索和上面的原理相同，此处不再赘述
        return User.query.join(followers, (followers.c.followed_id == User.id)).filter(followers.c.follower_id == self.id)



@login.user_loader   # login模块由__init__.py进行定义，见__init__.py的login = LoginManager()语句
def load_user(id):
    return User.query.get(int(id))



# 用户任务动态表Post
# 用户任务表表示用户发送的任务内容
class Post(db.Model):

    id = db.Column(db.Integer, primary_key = True)                              # 任务的id，Integer类型，作为表Post的主键，唯一确定一个特定的用户
    body = db.Column(db.String(160))                                            # 任务的描述内容，String类型
    timestamp = db.Column(db.DateTime, index=True)                              # 任务的时间戳
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))                   # 任务的创建者/发送者，这里使用的是SQLAlchemy的第一类db.relationship方法，db.Integer指定创建的新属性类型为Integer，db.Foreignkey()指定外键关系，这里创建的user_id参照User表的主键user_id
    filedir = db.Column(db.String(160))                                         # 任务原始视频的路径
    resultdir = db.Column(db.String(160))                                       # 任务处理结果视频的路径
    state = db.Column(db.Integer)                                               # 任务的当前状态，用户提交的每个任务仅有两种状态，state=0表示处于排队状态，state=1表示处于完成状态

    
    def __repr__(self):
        return '<Post %r>' % (self.body)

# 附注: 下面介绍一下上述代码中，两个表User和Post之间的关系，以及db.relationship的两类用法
#       1. User表和Post表的关系是，一个User可以关联多个Post，而一个Post仅能关联一个User
#       2. 由于上述的一对多关系，因此需要首先在多的一方Post中增加外键user_id，该外键参照User表的id属性，该操作使用第一类db.relationship方法实现，即: user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#       3. 由于上述的一对多关系，为了进一步方便访问，在一的一方User中，调用第二类db.relationship方法: posts = db.relationship('Post', backref='author', lazy='dynamic')，该方法配合上面的外键将Post和User连接起来，可以直接访问Post的author属性，访问发送该Post的用户对象User