from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import path, include
from error.views import custom_404, custom_500
from . import views

# カスタムエラーハンドラ
handler404 = custom_404
handler500 = custom_500

urlpatterns = [
    path('toamokuadmin/', admin.site.urls),
    path('', views.home , name="home"),
    path('accounts/', include('accounts.urls')),
    path('contact/', include('contact.urls')),
    path('dictionary/', include('dictionary.urls')),
    path('flashcard/', include('flashcard.urls')),
    path('test-error/', views.test_error, name='test_error'), # ERRORログ用
]