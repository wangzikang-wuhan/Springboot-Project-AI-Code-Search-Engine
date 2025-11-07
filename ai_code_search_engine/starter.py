import json

from code_cutting.springboot_project_parse import SpringBootParser
from constant.springboot_constant import project_name
from entity.template import ProjectType
from utils.resource_operations_util import open_in_explorer
from vectorization.qdrant_vector_memory import VectorHelper

class SearchEngineStarter:

    def __init__(self):
        self.vectorHelper = VectorHelper(project_name + "_coll")

    def loadProjectInVector(self,projectType: ProjectType):
        if projectType == ProjectType.SPRING_BOOT:
            results = SpringBootParser()
            self.vectorHelper.pushDataToVectorDB(results)


if __name__ == '__main__':
    vh = VectorHelper(project_name+"_coll")
    while True:
        question = input("请输入你要检索的内容: ")
        if question.lower() in ["exit", "quit"]:
            print("👋 再见！")
            break
        res = vh.mixtureSearch(question)
        if len(res) == 0:
            print("抱歉，没有找到任何结果")
        else:
            print("匹配到以下结果：")
            for r in res:
                data = r.__dict__ if hasattr(r, '__dict__') else r
                print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False))
                print("-" * 50)  # 分隔线
                #打开目录
                filePath = r["rootPath"].replace(r["fileName"], "")
                open_in_explorer(filePath)
















