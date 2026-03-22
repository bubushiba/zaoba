from PIL import Image, ImageDraw, ImageFont
import random, os, hashlib
from django.conf import settings



# 生成验证码
def Captcha():
    # 创建一个白色背景的图像
    img = Image.new(mode='RGB', size=(110, 30), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')
    captcha = ""

    # 生成 4 位验证码
    for i in range(4):
        a = random.randint(1, 3)
        if a == 1:
            s = chr(random.randint(48, 57))
        else:
            s = chr(random.randint(97, 112))
        captcha += s

    captcha_text = " ".join(str(i) for i in captcha)

    # 设置字体
    font = ImageFont.load_default().font_variant(size=25)
    draw.text([15, 0], captcha_text, 'blue', font=font)

    # 添加干扰线
    for _ in range(5):
        # 随机生成线的起点和终点坐标
        x1 = random.randint(0, 110)
        y1 = random.randint(0, 30)
        x2 = random.randint(0, 110)
        y2 = random.randint(0, 30)
        # 随机生成线的颜色
        line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)

    # 添加干扰点
    for _ in range(50):
        # 随机生成点的坐标
        x = random.randint(0, 110)
        y = random.randint(0, 30)
        # 随机生成点的颜色
        point_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.point([(x, y)], fill=point_color)

    return img, captcha


# 删除图片(任务表)
def task_image_del(datase, id):
    image = datase.objects.get(id=id)
    # 删除对应图片
    if image.demand_image:  # 检查任务是否有关联的图片文件
        if os.path.isfile(image.demand_image.path):  # 检查图片文件是否存在于文件系统中
            os.remove(image.demand_image.path)  # 如果文件存在，则删除该文件


# 删除图片(动态表)
def activity_image_del(datase, id):
    image = datase.objects.get(id=id)
    # 删除对应图片
    image_list = [image.image1, image.image2, image.image3]
    for img in image_list:
        if img:
            if os.path.isfile(img.path):  # 检查图片文件是否存在于文件系统中
                os.remove(img.path)  # 如果文件存在，则删除该文件


# 删除文件(作品表)
def production_file_del(datase, id):
    data = datase.objects.get(id=id)
    # 删除对应文件
    if data.file:
        if os.path.isfile(data.file.path):
            os.remove(data.file.path)  # 如果文件存在，则删除该文件


# 删除作品图片
def production_image_del(datase, id):
    datas = datase.objects.filter(production=id)
    for data in datas:
        if data.image:
            if os.path.isfile(data.image.path):
                os.remove(data.image.path)


# md5加密
def md5_data(data):
    key = settings.SECRET_KEY   # django自带的密钥
    obj = hashlib.md5(key.encode('utf-8'))
    obj.update(data.encode('utf-8'))
    return obj.hexdigest()
