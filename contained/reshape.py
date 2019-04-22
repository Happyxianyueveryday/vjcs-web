from PIL import Image

def reshape(filedir, resultdir):
    '''
    : reshape: 用于测试的算法，图像裁剪算法
    : param filedir: 原始图像文件的绝对路径
    : type filedir: str
    : param resultdir: 结果图像文件输出的绝对路径
    : type resultdir: str
    '''

    # 1. 从原始文件路径读取原始图像
    print('原始文件路径 = ', filedir)
    image = Image.open(filedir)

    # 2. 将图像进行略缩图化
    result = image.resize((256,256))

    # 3. 保存略缩图结果
    print('输出结果文件路径 = ', resultdir)
    result.save(resultdir)