from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import path, include
from error.views import custom_404, custom_500

# カスタムエラーハンドラ
handler404 = custom_404
handler500 = custom_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('contact/', include('contact.urls')),
    path('dictionary/', include('dictionary.urls')),
    path('flashcard/', include('flashcard.urls')),
]