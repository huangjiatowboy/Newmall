from rest_framework.pagination import PageNumberPagination


class MyPageNumberPagination(PageNumberPagination):
    """自定义分页"""
    page_size = 5  # 默认显示5条内容

    page_query_param = 'page'  # 查询关键字名称:第几页

    page_size_query_param = 'page_size'  # 查询关键字名称:每一页几条
