import os

#langsmith环境变量参数
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGSIMTH_KEY")
os.environ["LANGCHAIN_PROJECT"] = "local_zhipu_project"

#apikey
zhipu_ai_key = os.environ.get("ZHIPU_KEY")

#稠密向量
dense_vector_name = "dense"

#稀疏向量
sparse_vector_name = "sparse"

#向量模型 稠密向量 jina-embeddings-v2-base-code 解析代码专用
dense_model_name = "jinaai/jina-embeddings-v2-base-code"

#向量模型 稀疏向量
sparse_model_name = "prithivida/Splade_PP_en_v1"

#项目所在目录
project_base_path = "C:/Users/ADMIN/Desktop/"

#项目名称
project_name = "ai_springboot"

#java代码的路径
java_file_path = "/src/main/java"

#Springboot配置文件路径
config_file_path = "/src/main/resources"