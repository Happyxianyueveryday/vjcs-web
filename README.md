# vjcs-web

视频消除抖动算法的web端应用。
本应用为先行测试版，仅完成了基本功能，还存在安全性问题，稍后会更新正式版。

## 1. 构建和运行
  ### Step 1：安装本项目所依赖的库：
  本项目主要基于flask实现后端，使用HTML和扩展UI库bootstrap实现前端。项目本身的运行和部署需要使用下面的第三方库。
  
  ```
  $ pip install flask
  $ pip install flask-login
  $ pip install flask-openid
  $ pip install flask-sqlalchemy
  $ pip install sqlalchemy-migrate
  $ pip install flask-wtf
  $ pip install flask-babel
  $ pip install guess_language
  $ pip install flipflop
  $ pip install coverage
  $ pip install Flask-Mail
  ```
  
  ### Step 2：下载本项目文件
  点击本页面右上角的"Clone or Download" 按钮，下载本项目，也可以按照个人喜好使用git工具进行clone到本地。
  
  ### Step 3：修改邮箱地址
  因为本项目需要使用邮件功能，因此首先需要提供自己的邮箱，打开根目录下的config.py，重新设置如下的配置参数的值，提供自己的邮箱账号和授权码。  
  
  + 附注： 关于如何启动邮箱的SMTP功能并生成授权码，使用SSL还是TLS，以及域名及端口号问题，不同邮箱服务提供商的规定不同，请参考各个邮箱服务提供商的用户指引，下面的代码示例以qq邮箱为例。
  
  ```
  MAIL_SERVER = 'smtp.qq.com'
  MAIL_PORT = 465
  MAIL_USE_TLS = False
  MAIL_USE_SSL = True
  MAIL_DEBUG = True
  MAIL_USERNAME = ''  # qq邮箱账号
  MAIL_PASSWORD = ''  # qq邮箱授权码
  ```
  
  ### Step 5：在项目下载的路径下直接运行
  在下载的本项目的本地路径下运行run.py和run_algorithm.py脚本。
  
  ```
  $ python run.py
  $ python run_algorithm.py
  ```
  
  ### Step 6: 启动任意浏览器访问本机
  启动浏览器，地址栏输入"http://localhost:5000" 并访问。
  
  
  ## 2. 基本功能
  本项目的基本功能包括：
  
  + 用户账户注册，登录，登出
  + 编辑，提交处理任务
  + 取消已经提交的任务
  + 下载处理的结果文件
  + 邮件通知处理结果
  
  还有一些和本项目关系较小的可选功能：
  
  + 基于whoosh的文档全局搜索
  + 关注，取消关注用户
  + 生成关注的用户提交的任务动态
  
  本项目同样含有部分的功能尚待完成，即首页的功能介绍等，稍后再做确定和更新。
  
 
  ## 3. 项目结构
  本项目的项目结构如下所示，需要注意的是，此处只展示了重要的源代码部分。
  
  ```
  / -- |-- run.py: 可执行脚本文件
       |-- run_algorithm.py: 可执行脚本文件，同时执行该文件和上述的run.py即可运行本项目
       |-- contained: 算法容器文件夹，需要部署的算法以模块形式(.py文件)放入该文件夹
       |-- db_create.py: 数据库新建脚本
       |-- db_migrate.py: 数据库迁移脚本（使用方法：先迁移后更新）
       |-- db_update.py: 数据库更新脚本（使用方法：先迁移后更新）
       |-- config.py: 项目配置文件
       |-- container.py: 算法容器类
       |-- app --|
                 |-- templates: 包含flask模板(templates)的文件夹
                 |-- static: 包含用户上传的静态文件的文件夹
                 |-- __init__.py: 初始化文件
                 |-- forms.py: flask表单文件
                 |-- models.py: flask模型文件
                 |-- view.py: flask视图层文件
                 |-- redis_pubsub.py: redis发布者-订阅者模型队列，本项目中的可选的消息队列配置
                 |-- redis_queue.py: redis生产者-消费者模型队列，本项目默认使用的消息队列配置
  ```
  
  ## 4. 算法部署方法
  
  4月22日对算法容器部分进行了简单重写，目前提供一个基于反射机制的算法容器来实现算法的快速部署。下面简要介绍快速部署算法的基本方法：
  
  1. 部署算法文件：将需要部署的算法以模块文件(.py)的形式放入自定义的文件夹中。我们假设将要部署的算法以模块reshape.py的形式放在文件夹：C:\Users\PZH\Desktop\algorithm下。
  
  2. 初始化算法容器：给定上述自定义文件夹的绝对路径来初始化一个算法容器类Container的对象。
  
  ```
  from container import Container 
  container_path = 'C:\\Users\\PZH\\Desktop\\algorithm'
  container = Container(container_path)              # 初始化算法容器
  ```
  
  3. 获取算法对象：使用Container类的algorithm_contained方法来获取算法对象，该方法接受两个参数：modelname指定模块名，algoname指定算法对象名，该方法返回对应的算法对象，算法对象可以是一个函数或者是一个类。
  ```
  algofunc = container.algorithm_contained(modelname='reshape', algoname='reshape')  # 获取算法对象
  algofunc(source_dir, result_dir)     # 使用获得的算法对象（这里获得的算法对象是一个函数
  ```
  特别地，在本项目中，只需要打开根目录下的run_algorithm.py文件，修改第45~47行的代码的参数即可，原始代码如下所示。
  ```
  container_path = sys.path[0]+'\\'+'contained'
  container = Container(container_path)                                              # 初始化算法容器
  algofunc = container.algorithm_contained(modelname='reshape', algoname='reshape')  # 根据算法函数名获取函数对象，这里使用的测试算法函数是reshape模块的reshape算法函数
  ```
  
  
  ## 5. 后台异步处理
  因为考虑到具体部署时只有一台服务器，此版本使用的是简单的生产者-消费者模型的消息队列，本项目同样可以配置成使用发布者-订阅者模型工作。
  
  ## 6. 后期预告
  Android客户端接口稍后更新上线。
  
  
  
