from django.urls import path, include
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'user', views.UserViewSet, 'user')

# api routes
urlpatterns = [
    # path("login/", views.UserLoginAPIView.as_view(), name="user_login"),
    # path("register/", views.UserRegisterAPIView().as_view(), name="user_register"),
    # path("logout/", views.UserLogoutAPIView.as_view(), name="user_logout"),
    path("login/", views.LoginAPIView.as_view(), name="user_login"),
    # path("register/", views.register),
    # path("logout/", views.register),
    # path("user/", include(router.urls)),
]