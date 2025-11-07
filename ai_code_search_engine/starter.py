import json
from constant.constant import project_name
from vectorization.qdrant_vector_memory import VectorHelper

if __name__ == '__main__':
    # print("开始加载项目,过程会比较慢....")
    # results = SpringBootParser()
    vh = VectorHelper(project_name+"_coll")
    # print("开始插入数据")
    # vh.pushDataToVectorDB(results)
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















