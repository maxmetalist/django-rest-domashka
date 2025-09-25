from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class LessonPagination(PageNumberPagination):
    """Пагинатор для уроков"""

    page_size = 10  # Количество уроков на странице по умолчанию
    page_size_query_param = "page_size"
    max_page_size = 50


class CoursePagination(PageNumberPagination):
    """Пагинатор для курсов"""

    page_size = 5  # Количество курсов на странице по умолчанию
    page_size_query_param = "page_size"
    max_page_size = 20


class SubscriptionPagination(PageNumberPagination):
    """Пагинатор для подписок"""

    page_size = 10  # Количество подписок на странице по умолчанию
    page_size_query_param = "page_size"
    max_page_size = 30


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # количество элементов на странице
    page_size_query_param = "page_size"
    max_page_size = 100  # максимальное количество элементов на странице

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {"next": self.get_next_link(), "previous": self.get_previous_link()},
                "count": self.page.paginator.count,
                "results": data,
            }
        )
