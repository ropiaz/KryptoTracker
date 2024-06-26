# Author: Roberto Piazza
# Date: 07.04.2023

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

    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard-list'),

    path('portfolio-type/', views.PortfolioTypeAPIView.as_view(), name='portfolio-type-list'),
    path('portfolio-type/<int:pk>/', views.PortfolioTypeAPIView.as_view(), name='portfolio-type-detail'),

    path('portfolio/', views.PortfolioAPIView.as_view(), name='portfolio-list'),
    path('portfolio/<int:pk>/', views.PortfolioAPIView.as_view(), name='portfolio-detail'),

    path('asset-owned/', views.AssetOwnedAPIView.as_view(), name='asset'),

    path('transaction-type/', views.TransactionTypeAPIView.as_view(), name='transaction-list'),
    path('transaction-type/<int:pk>/', views.TransactionTypeAPIView.as_view(), name='transaction-detail'),

    path('transaction/', views.TransactionAPIView.as_view(), name='transaction-list'),
    path('transaction/<int:pk>/', views.TransactionDetailAPIView.as_view(), name='transaction-detail'),

    path('file-import-kraken/', views.KrakenFileImportAPIView.as_view(), name='file-import'),
    path('file-import-kiln/', views.KilnFileImportAPIView.as_view(), name='file-import-kiln'),

    path('exchange-api/', views.ExchangeApiAPIView.as_view(), name='exchange-api'),

    path('tax-report/', views.TaxReportAPIView.as_view(), name='tax-report'),
    path('tax-report/<int:pk>', views.TaxReportAPIView.as_view(), name='tax-report-detail'),

    # path("user/", include(router.urls)),
]
