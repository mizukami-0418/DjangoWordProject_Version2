# accounts/api_views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Q
from .models import CustomUser
from .serializers import (
    UserSerializer,
    UserProfileUpdateSerializer,
    CompleteProfileSerializer,
)
from dictionary.models import Word, Level
from flashcard.models import UserWordStatus


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    現在のユーザー情報を取得・更新

    GET /api/accounts/profile/
    - 現在のユーザー情報を取得

    PUT/PATCH /api/accounts/profile/
    - usernameを更新
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """PUT/PATCH: usernameの更新"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = UserProfileUpdateSerializer(
            instance, data=request.data, partial=partial
        )

        if serializer.is_valid():
            serializer.save()
            # 更新後の完全な情報を返す
            return Response(UserSerializer(instance).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(generics.RetrieveAPIView):
    """
    ユーザー詳細情報と学習統計を取得
    既存のuser_detail viewのAPI版

    GET /api/accounts/detail/
    - ユーザー基本情報
    - レベルごとの学習統計
    - モードごとの正解率
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # レベルとモードのリストを定義
        levels = Level.objects.all().values("id", "name")
        modes = ["en", "ja"]

        # ユーザーの回答実績を取得
        words_status = UserWordStatus.objects.filter(user=user)

        # モード名の翻訳マッピング
        MODE_TRANSLATIONS = {
            "en": "英訳",
            "ja": "和訳",
        }

        level_data = []
        for level in levels:
            level_id = level["id"]
            level_name = level["name"]

            # 各難易度の問題総数を取得
            total_count = Word.objects.filter(level=level_id).count()

            # 各モードごとの回答数と正解数
            mode_data = []
            for mode in modes:
                count = words_status.filter(word__level=level_id, mode=mode).count()
                correct = words_status.filter(
                    word__level=level_id, mode=mode, is_correct=True
                ).count()

                # 正解率を計算
                accuracy = round((correct / count * 100), 1) if count > 0 else 0

                mode_data.append(
                    {
                        "mode": mode,
                        "mode_display": MODE_TRANSLATIONS.get(mode, mode),
                        "count": count,
                        "correct": correct,
                        "accuracy": accuracy,
                    }
                )

            level_data.append(
                {
                    "id": level_id,
                    "name": level_name,
                    "total_count": total_count,
                    "modes": mode_data,
                }
            )

        response_data = {
            "user": UserSerializer(user).data,
            "levels": level_data,
        }

        return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_profile(request):
    """
    初回登録時のusername設定

    POST /api/accounts/complete-profile/
    {
        "username": "desired_username"
    }

    Supabase認証後、usernameが初期値（email由来）の場合に呼び出される
    """
    user = request.user
    serializer = CompleteProfileSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data["username"]

    # usernameが初期値（email由来、@を含む）の場合のみ更新可能
    if "@" in user.username:
        user.username = username
        user.save(update_fields=["username"])

        return Response(
            {
                "message": "プロフィールを設定しました",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": "ユーザー名は既に設定されています"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_profile_completion(request):
    """
    プロフィール設定状態を確認

    GET /api/accounts/check-profile/

    Returns:
        {
            "is_complete": true/false,
            "needs_username": true/false
        }
    """
    user = request.user

    # usernameに@が含まれている = 初期値 = 未設定
    needs_username = "@" in user.username

    return Response(
        {
            "is_complete": not needs_username,
            "needs_username": needs_username,
            "user": UserSerializer(user).data,
        }
    )
