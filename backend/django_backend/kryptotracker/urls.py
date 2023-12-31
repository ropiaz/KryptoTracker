from django.urls import path, include
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'user', views.UserViewSet, 'user')

# api routes
urlpatterns = [
    path("register/", views.UserRegisterAPI.as_view(), name="user_register"),
    path("logout/", views.LogoutAPI.as_view(), name="user_logout"),
    path("login/", views.LoginAPI.as_view(), name="user_login"),
    path("user-auth/", views.AuthUser.as_view(), name="user_auth"),
    path("user-edit/<str:token>", views.EditUser.as_view(), name="user_edit"),
    # path("user/", include(router.urls)),
]
