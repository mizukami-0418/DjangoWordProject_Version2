# accounts/management/commands/debug_jwt.py
# Supabase JWTをデバッグするコマンド

from django.core.management.base import BaseCommand
from django.conf import settings
import jwt
import json


class Command(BaseCommand):
    help = "Supabase JWTトークンをデバッグ"

    def add_arguments(self, parser):
        parser.add_argument("token", type=str, help="デバッグするJWTトークン")

    def handle(self, *args, **kwargs):
        token = kwargs["token"]

        self.stdout.write(self.style.WARNING("\n=== Supabase JWT デバッグ ===\n"))

        # 1. トークンのヘッダー部分をデコード（検証なし）
        try:
            header = jwt.get_unverified_header(token)
            self.stdout.write(self.style.SUCCESS("✅ トークンヘッダー:"))
            self.stdout.write(json.dumps(header, indent=2))
            self.stdout.write("")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ ヘッダーのデコード失敗: {str(e)}"))
            return

        # 2. トークンのペイロード部分をデコード（検証なし）
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            self.stdout.write(self.style.SUCCESS("✅ トークンペイロード（検証なし）:"))
            self.stdout.write(json.dumps(payload, indent=2, default=str))
            self.stdout.write("")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ ペイロードのデコード失敗: {str(e)}")
            )
            return

        # 3. 環境変数確認
        self.stdout.write(self.style.WARNING("環境変数:"))
        self.stdout.write(
            f"SUPABASE_JWT_SECRET: {'設定済み' if settings.SUPABASE_JWT_SECRET else '未設定'}"
        )
        if settings.SUPABASE_JWT_SECRET:
            self.stdout.write(f"長さ: {len(settings.SUPABASE_JWT_SECRET)} 文字")
        self.stdout.write("")

        # 4. アルゴリズムチェック
        alg = header.get("alg")
        self.stdout.write(self.style.WARNING(f"トークンのアルゴリズム: {alg}"))

        if alg != "HS256":
            self.stdout.write(
                self.style.ERROR(f"⚠️  警告: HS256 ではなく {alg} が使われています")
            )
        self.stdout.write("")

        # 5. 実際に検証を試みる
        self.stdout.write(self.style.WARNING("検証テスト:"))

        if not settings.SUPABASE_JWT_SECRET:
            self.stdout.write(
                self.style.ERROR("❌ SUPABASE_JWT_SECRET が設定されていません")
            )
            return

        try:
            # HS256で検証
            verified_payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
            self.stdout.write(self.style.SUCCESS("✅ HS256 での検証成功！"))
            self.stdout.write("")

        except jwt.InvalidAlgorithmError as e:
            self.stdout.write(self.style.ERROR(f"❌ アルゴリズムエラー: {str(e)}"))
            self.stdout.write(
                self.style.WARNING("対策: PyJWT のバージョンを確認してください")
            )
            self.stdout.write("pip install PyJWT==2.8.0")

        except jwt.ExpiredSignatureError:
            self.stdout.write(self.style.ERROR("❌ トークンの有効期限が切れています"))

        except jwt.InvalidAudienceError:
            self.stdout.write(self.style.ERROR("❌ audience が一致しません"))
            self.stdout.write(f"期待値: authenticated")
            self.stdout.write(f"実際の値: {payload.get('aud')}")

        except jwt.InvalidSignatureError:
            self.stdout.write(self.style.ERROR("❌ 署名が無効です"))
            self.stdout.write(
                self.style.WARNING("SUPABASE_JWT_SECRET が正しいか確認してください")
            )
            self.stdout.write("")
            self.stdout.write("Supabaseダッシュボード → Settings → API → JWT Secret")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 検証失敗: {str(e)}"))
            self.stdout.write(f"エラータイプ: {type(e).__name__}")
