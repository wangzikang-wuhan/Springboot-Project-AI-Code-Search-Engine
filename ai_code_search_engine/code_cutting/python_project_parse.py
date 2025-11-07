import ast

class PythonParseHelper:

    # 解析py文件返回所有的方法片段
    def pyCodeParse(self, content: str):
        return ""


if __name__ == '__main__':
    code = """
def getOtherType(self, fileName: str):
    config_file = [".properties",".yml",".yaml",".xaml",".xml"]
    #静态资源文件
    static_resource_file = [".html",".js",".css",".json",".jsp"]
    #取出文件后缀
    suffix = os.path.splitext(fileName)[1].lower()
    if suffix in config_file:
        return fileName+" 配置文件"
    elif suffix in static_resource_file:
        return fileName+" 静态资源文件"
    else:
        return "未识别出文件{}的类型".format(fileName)
    """.strip()
    tree = ast.parse(code)
    print(ast.dump(tree, indent=2))
