import os

#windows资源中打开文件
def open_in_explorer(path:str):
    if not os.path.exists(path):
        print("路径不存在")
        return
    if not os.path.isdir(path):
        print("不是一个目录")
        return
    os.startfile(path)
    print(f"已打开文件夹:{path}")

