# Built_in_function.py
###############
# 自定义函数文件 #
###############
def sumadd(a, b):
    a = int(a)
    b = int(b)
    # print(a+b)
    return int(a + b)


def stradd(a, b):
    a = str(a)
    b = str(b)
    return str((a + b))

def randomStr(base_str):
    _str = str(base_str)
    import random
    return _str+str(random.randint(1,10000))
