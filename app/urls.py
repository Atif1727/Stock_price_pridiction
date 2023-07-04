from django.urls import path
from . import views


urlpatterns = [
    path('',views.index,name='index'),
    path('search/', views.search),
    path('predict/<str:ticker_value>/<str:number_of_days>/', views.predict),
    path('ticker/', views.ticker)
]