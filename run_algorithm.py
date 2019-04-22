from app import app, db
from app.models import User, Post
from app.redis_queue import Consumer    # 导入消息队列
from datetime import datetime
from sqlalchemy.sql.expression import func
from werkzeug.utils import secure_filename
from flask import Flask
from flask_mail import Mail, Message
from container import Container    # 导入算法容器类
import sys, os
import redis
import time

# 本程序独立于flask核心框架之外，以独立进程的形式常驻服务器运行，因此规定放在app文件夹外
# 本程序主要完成如下的工作: 1. 从消息队列中及时出队一个任务，根据任务的id从数据库中查询该任务附带的原始文件位置，然后使用算法进行处理(特别注意，若数据库中查询不到对应的任务的项，则说明该任务已经被取消，这时直接处理下一个任务)
#                         2. 算法处理完成后，向发布该任务的用户回送一幅邮件表示视频消抖成功

if __name__ == "__main__":

    mail = Mail(app)

    consumer = Consumer(host='localhost', id=5)    # 创建与app.views模块中的生产者对应的消费者
    
    while True:

        # 1. 从消息队列中取出一个任务的id
        content = consumer.consume()    # 若redis消息队列中没有任务，则这时不能进行常见

        print(content)
        
        # 2. 在数据库中查询该任务的对应的文件名
        post = Post.query.filter(Post.id==content).first()

        if not post:      # 若数据库中不存在该任务，则说明用户在等待过程中已经取消任务，因此直接处理下一个任务
            continue
        else:             # 否则对用户任务中的视频文件进行处理，并返回一封邮件通知用户处理已经完成
            # 2.1. 根据数据库的查询结果，生成视频文件所在的路径，需要注意数据库中存储的是url而非路径，需要进行转化
            filename = post.filedir.split('/')[-1]                                       # 原始视频文件名
            filedir = app.config['UPLOAD_FOLDER']+'\\'+str(post.id)+'\\'+filename        # 生成原始视频路径
            resultdir = app.config['UPLOAD_FOLDER']+'\\'+str(post.id)+'\\'+'result.jpg'  # 生成结果视频的输出路径


            # 2.2. 调用算法容器，传入算法模块原始视频的路径和结果视频应该输出的路径
            # 暂定的规定是：结果视频保存在和原始视频同一文件夹下，命名为result.mp4，这里还需要考虑原始文件的命名
            container_path = sys.path[0]+'\\'+'contained'
            container = Container(container_path)                                              # 初始化算法容器
            algofunc = container.algorithm_contained(modelname='reshape', algoname='reshape')  # 根据算法函数名获取函数对象，这里使用的测试算法函数是reshape模块的reshape算法函数
            
            algofunc(filedir, resultdir)   # 调用算法函数


            # 2.3. 将处理结果的路径转换为url形式，保存在数据库Post表的resultdir字段中，并标记该任务已经处理完成
            resulturl = 'img'+'/'+str(post.id)+'/'+'result.jpg'    # 附注: 视频处理结果统一命名为result.mp4
            post.resultdir = resulturl
            post.state = 1                                         # 更改任务状态标记，表示任务已经处理完成
            db.session.commit()


            # 2.5. 向用户发送邮件，表示任务已经完成
            with app.app_context():     # 需要特别注意flask_email扩展中，发送邮件需要使用flask应用程序上下文
                message = Message("任务处理完成通知", sender="pzharima@qq.com", recipients=[post.author.email])
                message.body = "您好，您提交的任务(任务描述:"+post.body+")已经处理完成，处理结果请参见附件，也可以到网站主页上下载"  # 邮件正文
            
                with app.open_resource(resultdir) as fp:
                    message.attach("image.jpg", "image/jpg", fp.read())     # 处理结果作为附件加入邮件中

                mail.send(message)     # 发送邮件

            

            



            

    