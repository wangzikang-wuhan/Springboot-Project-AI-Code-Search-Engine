import os
from pathlib import Path
import javalang
from javalang.tree import ClassDeclaration
from constant.springboot_constant import project_name, project_base_path, java_file_path, config_file_path
from entity.template import ClassType, TypeEnum, CodeInfo
from llm import ai_helper

# java代码解析类
class JavaParseHelper:

    # 解析java文件返回所有的方法片段
    def javaCodeParse(self, content: str):
        try:
            # 解析java文件构造一个解析树 javalang把Java源码解析成语法树 如果文件语法不合规会抛出异常
            java_tree = javalang.parse.parse(content)
            # 把源码拆成一行一行的
            code_lines = content.splitlines()
            # 保存结果
            results = []
            # 遍历语法树
            for _, class_info in java_tree.filter(javalang.tree.ClassDeclaration):
                # 类名
                class_name = class_info.name
                # 遍历类方法
                for method in class_info.methods:
                    # 起始行号-1 就是该方法开始的上一行
                    start = method.position.line - 1
                    brace_count = 0
                    method_code_lines = []
                    found_start_brace = False
                    for i in range(start, len(code_lines)):
                        # 一整行的内容
                        line = code_lines[i]
                        method_code_lines.append(line)
                        # 检测花括号（统计平衡）当{}数量平衡时说明截取完成
                        brace_count += line.count('{')
                        brace_count -= line.count('}')
                        # 一旦找到第一个 '{' 开始计数
                        if '{' in line:
                            found_start_brace = True
                        # 括号计数归零说明方法结束
                        if found_start_brace and brace_count == 0:
                            break

                    method_code = "\n".join(method_code_lines)
                    results.append({
                        "class": class_name,
                        "start_line": start,
                        "method_name": method.name,
                        "method_code": method_code
                    })
            return results
        except Exception as e:
            print(e)
            return []

    # 检查java文件的类型
    def getType(self, content: str):
        if ClassType.CLASS.value in content:
            return TypeEnum.CLASS
        elif ClassType.ABSTRACT_CLASS.value in content:
            return TypeEnum.ABSTRACT_CLASS
        elif ClassType.ENUMERATE.value in content:
            return TypeEnum.ENUMERATE
        elif ClassType.INTERFACE.value in content:
            return TypeEnum.INTERFACE
        else:
            return TypeEnum.OTHER

    # 检查其他文件类型 配置文件 xml 等
    def getOtherType(self, fileName: str):
        #配置文件等
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

    # 解析java目录
    def javaPathAnalyze(self, path: str):
        # resources目录
        java = Path(path)
        # 当前目录下的直接子目录或者文件
        path_and_files = list(java.iterdir())
        #公共路径前缀
        java_path_prefix = project_base_path + project_name + java_file_path + "\\"
        # 记录结果
        results = []
        for item in path_and_files:
            if self.isFile(item):
                content = Path.read_text(item, encoding="utf-8")
                # 获取类型
                typeStr = self.getType(content)
                #获取包名
                package = str(item).replace(java_path_prefix, "").replace("\\",".").replace(".java","")

                #是否为实体类
                if typeStr == TypeEnum.CLASS:
                    # 判断是否为实体类
                    if self.isEntity(content):
                        info = self.parseFile(item=item,package=package)
                        results.append(info)
                    else:
                        # 不是实体类
                        methods_results = self.javaCodeParse(content)
                        # 取出数据并封装
                        for res in methods_results:
                            #基本数据直接填上去
                            info = CodeInfo(
                                rootPath=str(item),
                                content=res["method_code"],
                                fileName=item.name,
                                fileType=typeStr.value,
                                describe="",
                                filePackage=package,
                                projectName=project_name,
                                line_number=res["start_line"],
                            )
                            #开始调用LLM获取代码段描述
                            des = ai_helper.llmAnalyseCode(info)
                            info.describe = des
                            # 填充完毕大概长这样
                            # {
                            #   "rootPath": "C:\\Users\\ADMIN\\Desktop\\ai_springboot\\src\\main\\java\\com\\wzk\\ai_springboot\\AiSpringbootApplication.java",
                            #   "content": "    public static void main(String[] args) {\n        SpringApplication.run(AiSpringbootApplication.class, args);\n    }",
                            #   "fileName": "AiSpringbootApplication.java",
                            #   "fileType": "普通类",
                            #   "describe": "该代码片段的核心作用是作为Spring Boot应用程序的入口点，通过调用`SpringApplication.run()`方法启动名为`AiSpringbootApplication`的应用程序。它负责初始化Spring容器并加载应用所需的组件，使整个项目能够运行。",
                            #   "filePackage": "com.wzk.ai_springboot.AiSpringbootApplication",
                            #   "projectName": "ai_springboot",
                            #   "line_number": 8
                            # }
                            #插回结果中
                            results.append(info)

                elif typeStr == TypeEnum.ABSTRACT_CLASS:
                    # 是抽象类 一样要切割
                    methods_results = self.javaCodeParse(content)
                    if len(methods_results) == 0 or methods_results == []:
                        # 基本数据直接填上去
                        info = CodeInfo(
                            rootPath=str(item),
                            content=content,
                            fileName=item.name,
                            fileType=typeStr.value,
                            describe="",
                            filePackage=package,
                            projectName=project_name,
                        )
                        # 开始调用LLM获取代码段描述
                        des = ai_helper.llmAnalyseCode(info)
                        info.describe = des
                        # 插回结果中
                        results.append(info)
                    else:
                        # 取出数据并封装
                        for res in methods_results:
                            # 基本数据直接填上去
                            info = CodeInfo(
                                rootPath=str(item),
                                content=res["method_code"],
                                fileName=item.name,
                                fileType=typeStr.value,
                                describe="",
                                filePackage=package,
                                projectName=project_name,
                                line_number=res["start_line"],
                            )
                            # 开始调用LLM获取代码段描述
                            des = ai_helper.llmAnalyseCode(info)
                            info.describe = des
                            # 插回结果中
                            results.append(info)

                elif typeStr == TypeEnum.INTERFACE:
                    # 基本数据直接填上去
                    info = CodeInfo(
                        rootPath=str(item),
                        content=content,
                        fileName=item.name,
                        fileType=typeStr.value,
                        describe="",
                        filePackage=package,
                        projectName=project_name,
                    )
                    # 开始调用LLM获取代码段描述
                    des = ai_helper.llmAnalyseCode(info)
                    info.describe = des
                    # 插回结果中
                    results.append(info)
                else:
                    info = self.parseFile(item=item,package=package)
                    results.append(info)
            else:
                # 是目录直接递归
                sub_res = self.javaPathAnalyze(str(item))
                results.extend(sub_res)

        return results

    # 判断类是不是实体类
    def isEntity(self, content: str):
        try:
            tree = javalang.parse.parse(content)
            for _, node in tree.filter(ClassDeclaration):

                #检查注解
                annotation_names = {
                    #去掉前缀 @
                    ann.name.split(".")[-1]
                    for ann in getattr(node, "annotations", [])
                }

                #非实体类注解
                non_entity_annotations = {"Service", "Controller", "Repository", "Component", "Configuration",
                                          "RestController"}

                #只要包含非实体类注解一定不是实体类
                if annotation_names & non_entity_annotations:
                    return False

                #强实体类注解
                strong_entity_annotations = {"Entity","Table","Document","TableName","NoArgsConstructor","AllArgsConstructor"}

                #字段注解辅助判断
                field_annotations = {"TableId", "TableField"}

                #先判断强实体类注解 拥有这些注解的大概率是实体类
                if annotation_names & strong_entity_annotations:
                    return True

                # 检查字段
                fields = getattr(node, 'fields', [])
                if len(fields) == 0:
                    # 没有字段，不是实体类
                    return False
                else:
                    #有字段 获取字段注解
                    annotation_names = set()
                    for field in fields:
                        #字段注解名称列表
                        for anno in field.annotations:
                            annotation_names.add(anno.name)
                    intersection = annotation_names & field_annotations
                    if intersection:
                        return True

                # 检查方法
                methods = getattr(node, 'methods', [])
                if len(methods) == 0:
                    # 有字段但没有方法，是实体类
                    return True

                # 检查是否只有标准方法
                standard_method_prefixes = ['get', 'set', 'is']
                standard_method_names = ['toString', 'equals', 'hashCode', 'clone']
                for method in methods:
                    method_name = method.name
                    # 如果方法名不是以标准前缀开头，也不在标准方法列表中
                    if (not any(method_name.startswith(prefix) for prefix in standard_method_prefixes) and
                            method_name not in standard_method_names):
                        # 有业务方法，不是纯实体类
                        return False
                # 只有标准方法，是实体类
                return True
            return False
        except Exception as e:
            print(f"解析出现异常：{e}")
            return False

    # 解析resources目录内容
    def resourcesPathAnalyze(self, path: str):
        # resources目录
        resources = Path(path)
        # 当前目录下的直接子目录或者文件
        path_and_files = list(resources.iterdir())
        # 判断是文件还是目录
        results = []
        for item in path_and_files:
            if self.isFile(item):
                info = self.parseFile(item)
                results.append(info)
            else:
                # 递归继续向下
                sub_res = self.resourcesPathAnalyze(str(item))
                results.extend(sub_res)
        return results

    # 检查是否为文件
    def isFile(self, item: Path):
        if item.is_file():
            return True
        else:
            return False

    # 解析文件
    def parseFile(self, item: Path,package:str = ""):
        content = Path.read_text(item, encoding="utf-8")
        fileType = self.getType(content)
        info = CodeInfo(
            rootPath=str(item),
            content=content,
            fileName=item.name,
            fileType= self.getOtherType(item.name) if fileType == TypeEnum.OTHER else fileType.value,
            describe="",
            filePackage=package,
            projectName=project_name
        )
        return info

    # 读取pom文件
    def loadPomContent(self, base_path: str, project_name: str):
        pom_file_name = "pom.xml"
        pom_path = base_path + project_name + "\\" + pom_file_name
        pom = Path(pom_path)
        if pom.exists():
            content = pom.read_text(encoding="utf-8")
            return CodeInfo(
                projectName=project_name,
                rootPath=pom_path,
                content=content,
                fileType=self.getType(content).value,
                fileName=pom_file_name,
                describe="这是项目的依赖文件pom.xml",
                filePackage="",
            )
        else:
            print("pom.xml not found")
            return None

#解析器
def SpringBootParser():
    helper = JavaParseHelper()
    results = []
    try:
        results.append(helper.loadPomContent(base_path=project_base_path, project_name=project_name))
        results.extend(helper.resourcesPathAnalyze(project_base_path + project_name + config_file_path))
        results.extend(helper.javaPathAnalyze(project_base_path + project_name + java_file_path))
        return results
    except Exception as e:
        print(e)
        return results

#测试
if __name__ == "__main__":
    entity = """
    package com.wzk.ai_springboot.controller;
    import com.wzk.ai_springboot.entity.User;
    import com.wzk.ai_springboot.service.UserService;
    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.web.bind.annotation.PostMapping;
    import org.springframework.web.bind.annotation.RequestBody;
    import org.springframework.web.bind.annotation.RequestMapping;
    import org.springframework.web.bind.annotation.RestController;
    
    /**
     * @author wangzikang
     */
    @RestController
    @RequestMapping("/user")
    public class UserController {
    
        @Autowired
        private UserService userService;
    
        @PostMapping("/login")
        public String login(String username, String password) {
            return userService.login(username, password);
        }
    
        @PostMapping("/register")
        public String register(@RequestBody User user) {
            return userService.register(user);
        }
    
    }
    """
    helper = JavaParseHelper()
    # res = helper.isEntity(content=entity)
    # print(res)
    res = helper.getOtherType("AdvertisersMapper.xml")
    print(res)

