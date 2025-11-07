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

#稠密向量和稀疏向量召回的文档数
dense_number = 4
sparse_number = 4

#查询最终返回的结果数量
outcome_number = 2

#向量数据库连接路径
qdrant_collection_url = "http://localhost:6333/"