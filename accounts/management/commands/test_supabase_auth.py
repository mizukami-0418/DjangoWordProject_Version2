# accounts/management/commands/test_supabase_auth.py
# このファイルは accounts/management/commands/ ディレクトリに配置

from django.core.management.base import BaseCommand
from django.conf import settings
import jwt
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Supabase JWT認証のテスト用トークンを生成"

    def handle(self, *args, **kwargs):
        """
        テスト用のSupabase風JWTトークンを生成

        使用方法:
        python manage.py test_supabase_auth
        """

        if not settings.SUPABASE_JWT_SECRET:
            self.stdout.write(
                self.style.ERROR("SUPABASE_JWT_SECRET が設定されていません")
            )
            return

        # テスト用ペイロード
        payload = {
            "sub": "test-supabase-user-id-12345",  # Supabaseユーザーid
            "email": "test@example.com",
            "aud": "authenticated",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        # トークン生成
        token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

        self.stdout.write(self.style.SUCCESS("\n=== テスト用Supabase JWT トークン ==="))
        self.stdout.write(f"\n{token}\n")
        self.stdout.write(self.style.SUCCESS("\n使用方法:"))
        self.stdout.write(
            'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/accounts/profile/'
        )
        self.stdout.write("")
