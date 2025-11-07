from enum import Enum
import json

#枚举 .java文件类型
class ClassType(Enum):
    CLASS = "public class"
    ABSTRACT_CLASS = "public abstract class"
    INTERFACE = "public interface"
    ENUMERATE = "public enum"

#字符串类型枚举
class TypeEnum(Enum):
    CLASS = "普通类"
    ABSTRACT_CLASS = "抽象类"
    INTERFACE = "接口"
    ENUMERATE = "枚举类"
    OTHER = "不是.java文件"

#信息类 用于描述某一段代码来自哪里 describe你完全可以全部由AI来生成 但我这里先给个默认值避免后面向量化的时候出问题了
class CodeInfo:
    def __init__(self,rootPath:str,content:str,fileName:str,fileType:str,filePackage:str,projectName:str,describe:str = "默认值",line_number:int = 0):
        #具体路径
        self.rootPath = rootPath
        #内容
        self.content = content
        #文件名
        self.fileName = fileName
        #文件类型
        self.fileType = fileType
        #描述
        self.describe = describe
        #包
        self.filePackage = filePackage
        #项目
        self.projectName = projectName
        #起始行号
        self.line_number = line_number

    #转换成json
    def to_json(self):
        return json.dumps(self.__dict__,indent=2, ensure_ascii=False)

    #检查java文件的类型 粗略的检测
    def getType(self):
        if ClassType.CLASS.value in self.content:
            self.type = "普通类"
        elif ClassType.ABSTRACT_CLASS.value in self.content:
            self.type = "抽象类"
        elif ClassType.ENUMERATE.value in self.content:
            self.type = "枚举类"
        elif ClassType.INTERFACE.value in self.content:
            self.type = "接口"
        else:
            self.type = "不是.java文件"

class ProjectType(Enum):
    SPRING_BOOT = "springboot"
    PYTHON = "python"

