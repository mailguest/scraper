# numpy==2.1.2
# pandas==2.2.3
# matplotlib==3.9.2

# https://github.com/liqima/faiss_note/tree/master

import time
import numpy as np
import sys
import faiss
import matplotlib.pyplot as plt


# 构建向量数据库的数据
def build_data():
    np.random.seed(0) # 设置 numpy 随机数生成器的种子值
    data = []
    for i in range(n_data):
        data.append(
            np.random.normal(mu, sigma, d) # 均值为3，方差为0.1，维度为d 的正态分布
        )
    data = np.array(data).astype('float32')
    return data

# 构建查询向量的数据
def build_query():
    np.random.seed(12)
    query = []
    for i in range(n_query):
        query.append(
            np.random.normal(mu, sigma, d)
        )
    query = np.array(query).astype('float32')
    return query


# 查看第六个向量是不是符合正态分布
def test_data(data):
    plt.hist(data[5])
    plt.show()


# 向量数据库初始化数据
def init_data(data):
    """
    精确索引
    """
    index = faiss.IndexFlatL2(d)                        # 构建index
    print(f"index.is_trained is: {index.is_trained}")   # False时需要train
    index.add(data)                                     # 添加数据
    print(f"index.ntotal is: {index.ntotal}")           # index中向量的个数
    return index

def init_data_flat(data, nlist = 50):
    """
    倒排表快速索引
    在数据量非常大的时候，需要对数据做预处理来提高索引效率。一种方式是对数据库向量进行分割，划分为多个d维维诺空间，查询阶段，只需要将查询向量落入的维诺空间中的数据库向量与之比较，返回计算所得的k个最近邻结果即可，大大缩减了索引时间。
    :params:nlist 参数控制将数据集向量分为多少个维度空间；
    nprobe 参数控制在多少个维诺空间的范围内进行索引。
    """
    quantizer = faiss.IndexFlatL2(d)                    # 量化器
    index = faiss.IndexIVFFlat(
        quantizer, d, nlist, 
        faiss.METRIC_L2         # METRIC_L2计算L2距离, 或faiss.METRIC_INNER_PRODUCT计算内积
    )         
    # 倒排表索引类型需要训练
    print(f"index.is_trained is: {index.is_trained}")   # assert not index.is_trained  
    index.train(data)                                   # 训练数据集应该与数据库数据集同分布
    print(f"index.is_trained is: {index.is_trained}")   # assert index.is_trained
    index.add(data)
    print(f"index.ntotal is: {index.ntotal}")           # index中向量的个数
    return index

# 乘积向量量化索引
def init_data_fpq(data, m = 8, nlist = 50):
    """
    乘积量化索引
    精确索引和倒排表快速索引在index中都保存了完整的数据库向量，在数据量非常大的时候会占用太多内存，甚至超出内存限制。
    在faiss中，当数据量非常大的时候，一般采用乘积量化方法保存原始向量的有损压缩形式,故而查询阶段返回的结果也是近似的。
    :params:m 列方向划分个数，必须能被d整除
    """
    quantizer = faiss.IndexFlatL2(d)                    # 量化器
    index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 4) # 4 表示每个子向量被编码为 4 bits
    index.train(data)                                   # 训练数据集应该与数据库数据集同分布
    index.add(data)
    return index
    """
    实验发现，乘积量化后查询返回的距离值与真实值相比偏小，返回的结果只是近似值。
    查询自身时能够返回自身，但真实查询时效果较差，这里只是使用了正态分布的数据集，在真实使用时效果会更好，原因有：
    1.正态分布的数据相对更难查询，难以聚类/降维；
    2.自然数据相似的向量与不相似的向量差别更大，更容易查找；
    """

def query_data(query, index, nprobe):
    # 因为查询向量是数据库向量的子集，所以每个查询向量返回的结果中排序第一的是其本身，L2距离是0.
    start_time = time.time()
    k = 10                                  # 返回结果个数
    index.nprobe = nprobe                   # 选择n个维诺空间进行索引
    dis, ind = index.search(query, k)       # 查询其他数据的k个相似结果
    print(f"dis is: {dis}")                 # 升序返回每个查询向量的距离
    print(f"ind is: {ind}")                 # 升序返回每个查询向量的k个相似结果
    print(f"search time is: {time.time()-start_time}")

if __name__ == '__main__':
    sys.path.append('.')
    mu = 3          # 均值
    sigma = 0.1     # 方差
    d = 512         # 维数
    n_data = 20000  # 数据库向量的个数
    n_query = 10    # 查询向量的个数

    # 1. 构建向量数据库的数据
    data = build_data()
    # test_data(data)
    # 2. 构建查询向量的数据
    query = build_query()
    # 3. 初始化数据
    # index = init_data(data)
    # index = init_data_flat(data)
    index = init_data_fpq(data)
    # 4. 查询向量
    nprobe = 50 
    """
    通过改变nprobe的值，发现在nprobe值较小的时候，查询可能会出错，但时间开销很小，随着nprobe的值增加，精度逐渐增大，但时间开销也逐渐增加，当nprobe=nlist时，等效于IndexFlatL2索引类型。
    简而言之，倒排表索引首先将数据库向量通过聚类方法分割成若干子类，每个子类用类中心表示，当查询向量来临，选择距离最近的类中心，然后在子类中应用精确查询方法，通过增加相邻的子类个数提高索引的精确度。
    """
    # query_data(data[:5], index, nprobe) # 查询数据库向量的子集
    query_data(query, index, nprobe) # 查询数据是其他数据