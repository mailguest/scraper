from config.db import init_mongo, mongo as db
from utils import ArticleMapper, Article

def test_mongodb():
    init_mongo()
    # 创建 Mapper 实例
    article_mapper = ArticleMapper(db=db)

    # 创建文章实体
    article = Article(
        UUID="2e44e3db9da45e16bfeb0ea433d0b060",
        title="有钱没闲VS有闲没钱，美国K型经济有哪些影响？",
        content="文章内容...",
        content_short="简短描述",
        date="2024-11-12",
        source="WallStreetCN",
        uri="https://example.com",
        status="success"
    )

    # 插入文章
    success = article_mapper.insert_article(article)
    assert success, "插入文章失败"

    # 获取单篇文章
    retrieved_article = article_mapper.get_article_by_uuid(article.UUID)
    assert retrieved_article is not None, "获取文章失败"
    
    # 更新文章
    retrieved_article.title = "新标题"
    success = article_mapper.update_article(retrieved_article.UUID, retrieved_article)
    assert success, "更新文章失败"

    # 获取文章列表
    result = article_mapper.get_articles(page=1, per_page=10)
    assert len(result['items']) > 0, "获取文章列表失败"

    # 删除文章
    success = article_mapper.delete_article(article.UUID)
    assert success, "删除文章失败"

    db.close()
    print("测试完成")

    