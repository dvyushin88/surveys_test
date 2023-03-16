from django.contrib import admin
from django.urls import path

from api.views import *

urlpatterns = [
    path('surveys/', SurveyViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('surveys/<int:pk>/', SurveyViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    path('surveys/<int:pk>/version/<int:version_id>/', SurveyViewSet.as_view({'get': 'retrieve'})),
    path('surveys/<int:pk>/start/', SurveyViewSet.as_view({'get': 'start'})),
    path('surveys/<int:pk>/question-answer/', SurveyViewSet.as_view({'get':'retrieve', 'post': 'question_answer'})),
    
    path('admin/', admin.site.urls),
]
