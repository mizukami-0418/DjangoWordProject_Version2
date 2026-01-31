# accounts/api_urls.py

from django.urls import path
from .api_views import (
    UserProfileView,
    UserDetailAPIView,
    complete_profile,
    check_profile_completion,
)

app_name = "accounts_api"

urlpatterns = [
    # ユーザープロフィール取得・更新
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    # ユーザー詳細情報（学習統計含む）
    path("detail/", UserDetailAPIView.as_view(), name="user_detail"),
    # 初回登録時のusername設定
    path("complete-profile/", complete_profile, name="complete_profile"),
    # プロフィール設定状態の確認
    path("check-profile/", check_profile_completion, name="check_profile"),
]
