import os
from typing import List
from qdrant_client import models,QdrantClient
from tqdm import tqdm
from constant.config_constant import qdrant_collection_url, dense_vector_name, dense_model_name, sparse_vector_name, \
    sparse_model_name, dense_number, sparse_number, outcome_number
from constant.springboot_constant import project_name
from entity.template import CodeInfo


class VectorHelper:

    def __init__(self,collection_name:str):
        self.client = QdrantClient(url=qdrant_collection_url,)
        self.collection_name = collection_name
        self.creatVectorDB()

    #创建集合
    def creatVectorDB(self):
        #不存在才创建
        if not self.client.collection_exists(self.collection_name):
            # 再创建
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    # 稠密向量配置
                    dense_vector_name: models.VectorParams(
                        # 向量维度
                        size=self.client.get_embedding_size(dense_model_name),
                        # 计算方式
                        distance=models.Distance.COSINE
                    )
                },
                # 稀疏向量配置
                sparse_vectors_config={sparse_vector_name: models.SparseVectorParams()},
            )
            print("向量数据库{}创建完成".format(self.collection_name))

    #插入数据
    def pushDataToVectorDB(self,data:List[CodeInfo]):
        #记录向量化后的结果
        documents = []
        #载荷
        payload = []
        #向量化
        print("开始向量化")
        for item in data:
            #需要向量化的参数
            code = item.content
            describe = item.describe
            # 生成稠密向量
            dense_document = models.Document(text=code, model=dense_model_name)
            # 生成稀疏向量
            sparse_document = models.Document(text=describe, model=sparse_model_name)
            # 将两种向量插入到documents 每一个节点都是两个向量
            documents.append(
                {
                    dense_vector_name: dense_document,
                    sparse_vector_name: sparse_document,
                }
            )
            #插入载荷
            payload.append(item.__dict__)

            # 获取cpu核心数
            cpu = os.cpu_count()

        # 插入到集合
        print("开始插入集合")
        self.client.upload_collection(
            # 集合名称
            collection_name=self.collection_name,
            # 文档集合 tqdm开启进度条
            vectors=tqdm(documents,desc="上传向量"),
            # 载荷
            payload=payload,
            # 并行任务数 cpu核心的一半 可以加快插入的速度
            parallel=int(cpu / 2),
        )

    #混合检索
    def mixtureSearch(self,query:str):
        res = self.client.query_points(
            collection_name=self.collection_name,
            # 设置融合的方式
            query=models.FusionQuery(
                # 融合的方式
                fusion=models.Fusion.RRF,
            ),
            # 召回
            prefetch=[
                # 同时根据两个模型召回两份结果 然后再根据结果融合 融合的方式是上面定义的
                models.Prefetch(
                    # 使用的模型
                    query=models.Document(text=query, model=dense_model_name),
                    # 搜索的字段
                    using=dense_vector_name,
                    # 召回的文档数  调高召回的数量可以提升权重
                    limit=dense_number
                ),
                models.Prefetch(
                    query=models.Document(text=query, model=sparse_model_name),
                    # 搜索的字段
                    using=sparse_vector_name,
                    # 召回的文档数
                    limit=sparse_number
                ),
            ],
            #查询过滤
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="projectName",
                        #精确匹配
                        match=models.MatchValue(value=project_name)
                    )
                ]
            ),
            # 最终结果的数量
            limit=outcome_number,
        ).points
        # 只返回载荷
        metadata = [point.payload for point in res]

        return metadata









