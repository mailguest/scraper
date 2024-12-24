# 初始化 数据库模型

from .models.Article import Article
from .models.PromptTemplate import PromptTemplate
from .models.Dictionary import Dictionary
from .models.Namespace import Namespace
from .models.IpProxy import IpProxy
from .models.ScheduleJob import ScheduleJob

__all__ = [
    "PromptTemplate",
    "Article",
    "Dictionary",
    "Namespace",
    "IpProxy",
    "ScheduleJob"
]

# 导入数据库操作类
# from .mappers.ArticleMapper import ArticleMapper
# from .mappers.DictionaryMapper import DictionaryMapper
# from .mappers.NamespaceMapper import NamespaceMapper
# from .mappers.PromptTemplateMapper import PromptTemplateMapper
# from .mappers.TaskLogsMapper import TaskLogsMapper

# __all__.extend([
#     "ArticleMapper",
#     "DictionaryMapper",
#     "NamespaceMapper",
#     "PromptTemplateMapper",
#     "TaskLogsMapper"
# ])

# 导入枚举

from .enums.ModelEnum import ModelEnum, LLModel
from .enums.StatusEnum import StatusEnum

__all__.extend([
    "ModelEnum",
    "StatusEnum"
])