from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomPasswordChangeView, CustomPasswordResetView, CustomPasswordResetConfirmView


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('user/', views.user_home, name='user_home'),
    path('user/edit/', views.user_edit, name='edit'),
    path('user/detail/', views.user_detail, name='detail'),
    path('user/password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('user/password_change/done', views.password_change_done, name='password_change_done'),
    # パスワードリセットのためのURL
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]