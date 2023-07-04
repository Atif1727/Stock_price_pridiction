from django.urls import path
from . import views


urlpatterns = [
    path('',views.index,name='index'),
    path('ticker/',views.ticker,name='ticker'),
    path('search/',views.search,name='search')
]