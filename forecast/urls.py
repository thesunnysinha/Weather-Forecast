from django.urls import path
from . import views

urlpatterns = [
    path('', views.locations, name='home'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('signup/',views.signup,name='signup'),
    path('profile/',views.profile,name='profile'),
]
