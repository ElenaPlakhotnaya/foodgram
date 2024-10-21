from rest_framework.pagination import PageNumberPagination

from users.constants import PAGE_SIZE


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = PAGE_SIZE
