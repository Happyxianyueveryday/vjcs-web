from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegisterForm, SubmitForm, ManageForm, SearchForm
from app.models import User, Post
from app.redis_queue import Producer
from datetime import datetime
from sqlalchemy.sql.expression import func
from werkzeug.utils import secure_filename
import os
import shutil
import redis

producer = Producer(host='localhost', id=5)

@app.before_request
def before_request():
    g.user = current_user
    


@app.route('/')
def index():
    '''
    : index: 路由到应用首页
    '''
    return render_template("index.html",title='首页', isuser=current_user.is_authenticated)   # 在HTML文件中使用{{}}包含的即为模板形参，flask.render_template使用实参替换这些形参



@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    : login: 路由到用户登录页面，进行用户登录
    '''
    if current_user.is_authenticated:    # 若用户已经登录，则直接重定向至用户个人主页'my_homepage'，并提示用户不要重复登录，current_user.is_authenticated()检测用户是否已经登录
        flash('您已经登录，请不要重复登录')
        return redirect(url_for('index'))# redirect是跳转至对应的路由函数，render_template是直接渲染网页，两者不相同

    form = LoginForm()                   # 创建LoginForm对象，LoginForm类定义参见forms.py，LoginForm={username, password, remember_me, submit}

    if form.validate_on_submit():        # 若用户登录时输入的用户名和密码合法，则进一步在数据库中检索用户名和密码是否正确
        # 附注: 
        # (1) ORM框架SQLAlchemy将数据库中的每一个表映射到一个python对象上，将表中的每一列映射到python对象的一个成员上，将表中的每一行(即每一个表项)映射到一个python对象的示例上
        # (2) ORM框架SQLAlchemy的教程请参见:https://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/0014021031294178f993c85204e4d1b81ab032070641ce5000

        user = User.query.filter(User.username==form.username.data).first()  # 在User对象下调用query.filter_by方法，因此返回的对象也是User对象的实例，参数中填匹配条件，.first()子调用指定只返回符合条件的第一个表项(实际上username为外键，因此最多智能查找一个符合条件的表项)
        
        if user and user.check_password(form.password.data):  # 若用户存在，且查找到的表项的密码和输入一致，则登录成功
            login_user(user, remember=form.remember_me.data)      # 调用第三方库内置方法login_user进行登录，remember形参直接初始化为用户表单上填写的内容form.remember_me.data，该参数决定是否保存cookie以维持登录状态

            flash('已登录成功!')

            # 登录成功，跳转至下一个页面
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')    # 路由到应用首页
            return redirect(next_page) 

        else:                             # 否则，登录失败，显示flash提示信息，然后重定向至当前登录页面
            flash('用户名或者密码不正确')
            return redirect(url_for('login'))
    
    return render_template('login.html', title='登录', form=form, isuser=current_user.is_authenticated)



@app.route('/logout')
def logout():
    '''
    : logout: 登出路由
    '''
    logout_user()
    flash('退出登录成功')
    return redirect(url_for('index'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    : register: 路由到用户注册页面，进行新用户注册
    '''

    form=RegisterForm()                  # 创建RegisterForm对象，RegisterForm类定义参见forms.py，RegisterForm={username, email, password, password_repeat, submit}

    # RegisterForm.validate_on_submit()方法将同时使用自定义的验证方法RegisterForm.validate_username和RegisterForm.validate_email进行验证
    # 从而保证了注册的账户名称username和账户邮箱email的唯一性
    if form.validate_on_submit():        
        same_user = User.query.filter(User.username==form.username.data).first()
        same_user_2 = User.query.filter(User.email==form.email.data).first()

        if not same_user and not same_user_2:
            user = User(username=form.username.data, email=form.email.data)      # 创建新用户对象
            user.set_password(form.password.data)                                # 设置新用户的对象的密码成员，服务器端不应该保存用户的原始密码，具体参见model.py中的User.set_password方法的说明
            db.session.add(user)                                                 # 创建向数据库中增加新User对象的事务
            db.session.commit()                                                  # 提交事务，正式在数据库中增加新用户的项

            flash('账号注册成功！现在可以进行登录')
            return redirect(url_for('login'))
        
        elif same_user:
            flash('该用户名已经被注册，请换用不同的用户名')
            return redirect(url_for('register'))

        elif same_user_2:
            flash('该邮箱已经被注册，请换用不同的邮箱')
            return redirect(url_for('register'))
    
    return render_template('register.html', title='注册', form=form, isuser=current_user.is_authenticated)



@app.route('/my_homepage/<username>')        # 这里使用的装饰器略有不同，<username>表示将url中'my_homepage/'后的部分作为参数传入my_homepage路由函数中
@login_required
def my_homepage(username):
    '''
    : my_homepage: 路由到用户个人主页，完成个人主页的个人信息显示和关注的动态显示
    '''
    # 1. 从数据库中查询用户基本信息
    user = User.query.filter_by(username=username).first()

    # 2. 从数据库中查询用户关注的人动态
    posts=g.user.followed_posts()   # 直接调用User表的followed_posts方法获得关注的动态，该函数的实现请参见'/app/models.py'

    # 3. 从数据库中查询该用户所发表的全部动态
    my_posts=Post.query.filter(Post.user_id==user.id).all()

    # 4. 从数据库中查找该用户关注的所有的人以及该用户的所有粉丝
    followed=g.user.followed_list()
    follower=g.user.follow_list()
    
    return render_template('my_homepage.html', user=user, posts=posts, my_posts=my_posts, isuser=current_user.is_authenticated, followed=followed, follower=follower)



@app.route('/addweibo', methods=['GET', 'POST'])
@login_required
def addweibo():
    '''
    : addweibo: 增加一条任务
    '''
    form=SubmitForm()    # 生成任务编写表单

    if form.validate_on_submit():  # 若用户输入了合法的任务内容，则将用户的任务发送到数据库中

        # 1. 从表单中收集任务编写内容
        f = form.file.data   
        filename = secure_filename(f.filename)   # filename一般可以伪装，因此必须使用secure_filename来进行处理

        post=Post(body=form.body.data, user_id=current_user.id, timestamp=datetime.utcnow(), state=0) 

        # 2. 将新的任务加入数据库的Post表单中
        db.session.add(post)
        db.session.commit()

        # 3. 将任务上传的视频保存到对应的文件夹: /weibofile/<weibo_id>
        save_dir=app.config['UPLOAD_FOLDER']+'\\'+str(post.id)
        os.mkdir(save_dir)
        f.save(os.path.join(save_dir, filename))

        tar_post=Post.query.filter(Post.id==post.id).first()
        tar_post.filedir='img'+'/'+str(post.id)+'/'+filename
        db.session.commit()

        # 4. 将新的任务的id加入消息队列
        producer.produce(post.id)

        # 5. 提示用户信息，并跳转至应用首页
        flash('任务已成功提交')
        return redirect(url_for('index'))

    return render_template('addweibo.html', form=form, title='新任务', isuser=current_user.is_authenticated)



@app.route('/delweibo/<id>',methods=['GET','POST'])
@login_required
def delweibo(id):
    '''
    : delweibo: 删除一条指定id的任务
    '''
    # 1. 首先查找到目标任务的表项，检查用户要删除的任务id是否是该用户自身的
    post=Post.query.filter(Post.id==id).first()     # 查找到的目标任务
    
    if post.user_id==current_user.id:    # 若用户需要删除自己的任务，则允许删除
        db.session.delete(post)
        db.session.commit()

        flash('任务成功取消')

        # 最后删除该任务对应的图片或者视频文件
        save_dir=app.config['UPLOAD_FOLDER']+'\\'+str(id)
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)

        return redirect(url_for('index'))
    
    else:                                # 若用户通过修改url的方式试图删除其他人的任务，则禁止删除，并显示警告信息
        flash('警告: 您不能删除其他用户提交的任务')
        return redirect(url_for('index'))



@app.route('/management/<username>',methods=['GET','POST'])
@login_required
def management(username):
    '''
    : management: 用户个人账户信息管理
    '''

    # 1. 首先在数据库中查找用户名为username的表项
    user = User.query.filter(User.username==username).first()
    user_data={'username':user.username, 'email':user.email, 'description':user.description, 'sign':user.sign, 'job':user.job, 'location':user.location}

    # 2. 从表单中读取用户的输入的账户的更新信息
    form=ManageForm()

    if form.validate_on_submit():
        user.description=form.description.data
        user.sign=form.sign.data
        user.location=form.location.data
        user.job=form.job.data
        db.session.commit()

        flash('个人账户信息更新成功')

    return render_template('management.html', title='个人账户信息管理', user=user, form=form, isuser=current_user.is_authenticated)



@app.route('/search',methods=['GET','POST'])
@login_required
def search():
    '''
    : search: 搜索页面路由
    '''

    # 1. 从表单中读取用户输入的搜索关键字
    form=SearchForm()

    if form.validate_on_submit():
        target=form.target.data    # 读取用户输入的搜索关键字
        return redirect(url_for('search_result', target=target))    # 将搜索关键字作为url的一部分参数重定向到search_result路由函数，由search_result来生成查询结果
        
    return render_template('search.html', isuser=current_user.is_authenticated, title='全局搜索', form=form)



@app.route('/search_result/<target>',methods=['GET','POST'])
@login_required
def search_result(target):
    '''
    : search_result: 搜索查询和结果显示路由
    '''

    # 1. 这里使用whoosh出现问题，因此直接使用sql查询进行解决
    users = User.query.filter(User.username.like('%'+target+'%')).all()
    posts = Post.query.filter(Post.body.like('%'+target+'%')).all()

    return render_template('search_result.html', isuser=current_user.is_authenticated, target=target, posts = posts, users = users)



@app.route('/follow/<username>', methods=['GET','POST'])
@login_required
def follow(username):
    '''
    : follow: 关注某个用户
    '''
    # 0. 首先判断用户要关注的人是否为自己，本系统中不允许关注自己
    if username==current_user.username:
        flash('您不能关注自己')
        return redirect(url_for('index'))

    # 1. 首先查找需要关注的用户名
    user = User.query.filter(User.username==username).first() 

    # 2. 然后根据查找结果确定是否进行关注操作
    if not user:             # 2.1 若查找结果为空，则不能进行关注
        flash('未找到该用户')
        return redirect(url_for('index'))
    else:                    # 2.2 若能查找到结果，则可以进行关注
        u = g.user.follow(user)   # 调用sqlachemey数据库实现的follow方法进行关注，该方法的具体实现见'/app/models.py'
        if u is None:
            flash('不能进行关注')
            return redirect(url_for('index'))
        db.session.add(u)
        db.session.commit()
        flash('成功关注该用户')
        return redirect(url_for('index'))



@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    '''
    : unfollow: 取消关注某个用户
    '''
    # 0. 首先判断用户要取消关注的人是否为自己，本系统中不允许关注和取消关注自己
    if username==current_user.username:
        flash('您不能取消关注自己')
        return redirect(url_for('index'))

    # 1. 首先查找需要取消关注的用户名
    user = User.query.filter(User.username==username).first()

    # 2. 然后根据查找结果确定是否进行取消关注操作
    if user is None:
        flash('未找到该用户')
        return redirect(url_for('index'))
    else:
        u = g.user.unfollow(user)

        if u is None:
            flash('不能进行取消关注')
            return redirect(url_for('index'))
        db.session.add(u)
        db.session.commit()
        flash('已经取消关注该用户')
        return redirect(url_for('index'))


        

    
    




    
    


    
    
    
