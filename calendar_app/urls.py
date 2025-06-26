from django.urls import path
from . import views

app_name = 'calendar_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('auth/callback/', views.callback, name='callback'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('logout/', views.logout_view, name='logout'),
]