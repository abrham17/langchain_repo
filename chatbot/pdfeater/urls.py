from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload_and_process/', views.upload_and_process, name='upload_and_process'),
    path('get_answer/', views.get_answer, name='get_answer'),
]
