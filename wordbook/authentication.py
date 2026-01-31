# config/authentication.py

from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class SupabaseAuthentication(authentication.BaseAuthentication):
    """
    Supabase JWTトークンを検証し、CustomUserを取得または作成する認証バックエンド

    使用方法:
    1. リクエストヘッダーに `Authorization: Bearer <supabase_jwt>` を含める
    2. JWTを検証し、supabase_idでユーザーを取得または作成
    3. 既存のセッション認証と並行して動作
    """

    def authenticate(self, request):
        """
        認証処理のメインロジック

        Returns:
            tuple: (user, token) または None
        """
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header:
            return None

        try:
            # "Bearer {token}" から token を抽出
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return None

            token = parts[1]

            # Supabase JWTを検証
            payload = self._verify_jwt(token)

            # ユーザーを取得または作成
            user = self._get_or_create_user(payload)

            return (user, token)

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise exceptions.AuthenticationFailed("トークンの有効期限が切れています")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise exceptions.AuthenticationFailed("無効なトークンです")
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise exceptions.AuthenticationFailed(f"認証に失敗しました: {str(e)}")

    def _verify_jwt(self, token):
        """
        Supabase JWTを検証

        Args:
            token (str): JWTトークン

        Returns:
            dict: デコードされたペイロード
        """
        if not settings.SUPABASE_JWT_SECRET:
            raise exceptions.AuthenticationFailed(
                "Supabase JWT Secretが設定されていません"
            )

        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )

        return payload

    def _get_or_create_user(self, payload):
        """
        JWTペイロードからユーザーを取得または作成

        Args:
            payload (dict): デコードされたJWTペイロード

        Returns:
            CustomUser: ユーザーオブジェクト
        """
        supabase_user_id = payload.get("sub")
        email = payload.get("email")

        if not supabase_user_id or not email:
            raise exceptions.AuthenticationFailed(
                "トークンに必要な情報が含まれていません"
            )

        # supabase_idでユーザーを取得または作成
        user, created = User.objects.get_or_create(
            supabase_id=supabase_user_id,
            defaults={
                "email": email,
                "username": email.split("@")[
                    0
                ],  # 仮のusername（後でフロントエンドから更新）
            },
        )

        if created:
            logger.info(f"New user created via Supabase: {email}")

        # メールアドレスが変更されている場合は更新
        if user.email != email:
            logger.info(f"Updating email for user {user.id}: {user.email} -> {email}")
            user.email = email
            user.save(update_fields=["email"])

        return user

    def authenticate_header(self, request):
        """
        認証失敗時のWWW-Authenticateヘッダー
        """
        return 'Bearer realm="api"'
