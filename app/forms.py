from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileAllowed, FileRequired
from app.models import User

# 本文件(forms.py)包含项目中所使用的各种flask表单

# 关于flask表单的基本用法可以参见: http://www.bjhee.com/flask-ext7.html

class LoginForm(FlaskForm):
    '''
    : LoginForm: flask登录表单
    '''
    username = StringField('用户名', validators=[DataRequired()])          # username: 用户名字段，validators参数列表指定该字段的验证方式，选用的DataRequired()验证方式保证用户输入不为空
    password = PasswordField('密码', validators=[DataRequired()])        # password: 密码字段
    remember_me = BooleanField('记住我')                                # remember_me: 勾选框字段
    submit = SubmitField('登录')                                             # submit: 提交按钮字段


class RegisterForm(FlaskForm):
    '''
    : RegisterForm: flask注册表单
    '''
    username = StringField('用户名', validators=[DataRequired()])          # username: 注册用户名字段
    email = StringField('邮箱', validators=[DataRequired(), Email()])       # email: 邮箱字段，validators参数指定验证方式，DataRequired()验证保证用户输入非空，Email()验证保证用户输入为标准邮箱地址格式
    password = PasswordField('密码', validators=[DataRequired()])        # password: 注册密码字段
    password_repeat = PasswordField('重复输入密码', validators=[DataRequired(), EqualTo('password')])   # password_repeat: 重复密码字段，validators参数指定验证方式，DataRequired()验证保证用户输入非空，EqualTo('password')验证保证输入的密码与第一次输入的密码字段password相同
    submit = SubmitField('注册')                                             # submit: 提交按钮字段

class SubmitForm(FlaskForm):
    '''
    : SubmitForm: flask提交新任务表单
    '''
    body=StringField('任务说明', validators=[DataRequired()])          # body: 微博正文字段
    # 附注: 需要特别注意，上传图片或者视频时，validators必须使用FileRequired()
    file=FileField('上传图片或者视频', validators=[FileRequired()])            # file: 微博视频片段，这里不限定上传的类型，但是只有视频或者图片能够显示出来
    submit = SubmitField('发布任务')                                          # submit: 提交按钮字段

class ManageForm(FlaskForm):
    '''
    : ManageForm: 管理用户个人信息的表单
    '''
    description = StringField('自我介绍', validators=[DataRequired()])       # description: 该用户的自我介绍和描述，String类型
    sign = StringField('签名', validators=[DataRequired()])                     # sign: 用户个性签名
    job = StringField('职业', validators=[DataRequired()])                       # job: 用户职业
    location = StringField('住址', validators=[DataRequired()])             # location: 用户的所在地址
    submit = SubmitField('更新个人信息')                                                # submit: 提交按钮字段

class SearchForm(FlaskForm):
    '''
    : SearchForm: 全局搜索表单
    '''
    target = StringField('搜索关键字', validators=[DataRequired()])                     # target: 搜索关键字输入字段
    submit = SubmitField('全局搜索')                                                # submit: 提交按钮字段

    
    
    
