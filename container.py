import sys, os
import importlib

# 算法容器类: 最终需要部署的算法，只需放入contained文件夹，然后使用此类进行加载，该类用于实现面向对象编程的反射过程
class Container:
    
    def __init__(self, pathname):
        '''
        : __init__: 初始化算法容器
        : param pathname: 算法容器的绝对路径，一个算法容器就是一个文件夹，其中包含多个算法模块文件
        : type pathname: str
        '''
        self.pathname = pathname          # 记录算法容器的具体路径

        return 

    def algorithm_contained(self, modelname, algoname):
        '''
        : algorithm_contained: 获取指定名称的算法函数
        : param modelname: 算法函数所在的模块名
        : type algoname: str
        : param algoname: 算法函数名
        : type algoname: str
        : return: 指定的目标算法函数
        : rtype: function
        '''
        sys.path.append(self.pathname)

        obj = __import__(modelname)

        if hasattr(obj, algoname):
            return getattr(obj, algoname)
        else:
            return None

        

    