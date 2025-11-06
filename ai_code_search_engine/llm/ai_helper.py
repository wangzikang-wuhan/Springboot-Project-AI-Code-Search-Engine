from typing import TypedDict
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from constant.constant import zhipu_ai_key
from langgraph.graph import START, StateGraph
from entity.template import CodeInfo

#zhipu
llm = ChatZhipuAI(
    api_key=zhipu_ai_key,
    model="glm-4.5"
)

#状态
class State(TypedDict):
    projectName:str
    content:str
    fileName:str
    fileType:str
    path:str
    describe: str

#提示词模板
prompt_template = PromptTemplate.from_template(
    """
    你是一名资深的Java开发者，熟悉Spring Boot项目结构。
    请根据以下信息，用一段话简洁描述该代码片段的核心作用。
    只描述实际功能，不要编造未出现的内容。
    项目信息：
    -项目名称:{projectName}
    -文件名称:{fileName}
    -文件类型:{fileType}
    -具体路径:{path}
    
    代码内容：
    {content}
    """
)

#定义结构化的输出并填充提示词调用llm返回结果
def fullPromptAndCall(state: State):
    #填充提示词内容
    prompt = prompt_template.invoke({
        "projectName":state["projectName"],
        "content":state["content"],
        "fileName":state["fileName"],
        "fileType":state["fileType"],
        "path":state["path"],
    })
    #调用llm
    des = llm.invoke(prompt)
    #填充到状态里
    return {"describe":des.content}

#创建一个带类型State的图构建器
graph_builder = StateGraph(State)
#添加节点
graph_builder.add_node("fullPromptAndCall",fullPromptAndCall)
#开始节点
graph_builder.add_edge(START, "fullPromptAndCall")
# 启用内存持久化（支持多用户）
memory = MemorySaver()
#构造一个graph
graph = graph_builder.compile(checkpointer=memory)

#对外提供一个访问LLM获取代码分析的方法
def llmAnalyseCode(codeInfo:CodeInfo)->str:
    try:
        # 相同的项目使用同一个缓存
        config = {
            "configurable":
                {
                    # thread_id用于状态管理 这里使用项目名称的hash值
                    "thread_id": codeInfo.projectName.__hash__()
                }
        }
        # 初始状态
        init_state = State()
        init_state["projectName"] = codeInfo.projectName
        init_state["content"] = codeInfo.content
        init_state["fileName"] = codeInfo.fileName
        init_state["fileType"] = codeInfo.fileType
        init_state["path"] = codeInfo.rootPath
        # 调用模型返回结果
        res = graph.invoke(init_state, config)
        return res["describe"]
    except Exception as e:
        print(e)
        return "LLM未分析到任何结果"




