from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import path, include
from error.views import custom_404, custom_500
from . import views
from django.http import JsonResponse

# カスタムエラーハンドラ
handler404 = custom_404
handler500 = custom_500


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("contact/", include("contact.urls")),
    path("dictionary/", include("dictionary.urls")),
    path("flashcard/", include("flashcard.urls")),
    path("test-error/", views.test_error, name="test_error"),  # ERRORログ用
    path("api/health/", health_check),
    path("api/", include("dictionary.api.urls")),
    # ===== 🆕 DRF API用URL =====
    path("api/accounts/", include("accounts.api_urls")),
    path("api/dictionary/", include("dictionary.api_urls")),
    path("api/flashcard/", include("flashcard.api_urls")),
    path("api/contact/", include("contact.api_urls")),
]
