from django.urls import path
from .views import FloorList, FloorDetail, RoomDetail, StatusList, BookWorkplace, BookMultipleWorkplaces, \
    GenerateStatuses

urlpatterns = [
    path('floor/', FloorList.as_view()),
    path('floor/<int:pk>/', FloorDetail.as_view()),
    path('room/<int:pk>/', RoomDetail.as_view()),
    path('status/', StatusList.as_view()),
    path('book/<int:pk>/', BookWorkplace.as_view()),
    path('book/multiple/', BookMultipleWorkplaces),

    path('generate_statuses/', GenerateStatuses),
]
