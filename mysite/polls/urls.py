from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/<str:order>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/<str:order>/',
         views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/<str:order>/', views.vote, name='vote'),
]
