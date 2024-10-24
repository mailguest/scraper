import pytest
from scripts.wallstreetcn_scraper import WallStreetCNContentScraper

@pytest.fixture
def scraper():
    # 初始化 WallStreetCNContentScraper 实例
    # 使用提供的 URL 进行测试
    test_uri = "https://wallstreetcn.com/articles/3731227"
    return WallStreetCNContentScraper(test_uri)

def test_scrape_content(scraper):
    # import pdb
    # pdb.set_trace()

    # 调用 scrape_content 方法
    content = scraper.scrape()
    print(content)
    # 检查返回的内容是否为空
    assert content is not None, "The content should not be None."
    assert len(content) > 0, "The content should have more than 0 characters."
    print(f"Scraped content: {content[:100]}...")  # 仅打印前100个字符作为示例


# pytest -s tests/test_scraper.py
# import pdb
# pdb.set_trace()