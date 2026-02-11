# accounts/management/commands/check_jwt_secret.py
# SUPABASE_JWT_SECRET の設定を確認するコマンド

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "SUPABASE_JWT_SECRET の設定を確認"

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.WARNING("\n=== SUPABASE_JWT_SECRET チェック ===\n")
        )

        if not settings.SUPABASE_JWT_SECRET:
            self.stdout.write(
                self.style.ERROR("❌ SUPABASE_JWT_SECRET が設定されていません")
            )
            return

        secret = settings.SUPABASE_JWT_SECRET

        # 基本情報
        self.stdout.write(
            self.style.SUCCESS("✅ SUPABASE_JWT_SECRET が設定されています")
        )
        self.stdout.write(f"長さ: {len(secret)} 文字\n")

        # 最初の100文字を表示
        self.stdout.write(self.style.WARNING("最初の100文字:"))
        self.stdout.write(f"{secret[:100]}...\n")

        # PEM形式かチェック
        if "-----BEGIN" in secret:
            self.stdout.write(
                self.style.SUCCESS("✅ PEM形式の公開鍵のようです (ES256用)\n")
            )

            # 改行の状態をチェック
            if "\\n" in secret:
                self.stdout.write(
                    self.style.WARNING("⚠️  \\n が文字列として含まれています")
                )
                self.stdout.write(
                    "   → これは正常です。Djangoが自動的に改行に変換します\n"
                )
            elif "\n" in secret:
                self.stdout.write(self.style.SUCCESS("✅ 実際の改行が含まれています\n"))
            else:
                self.stdout.write(self.style.ERROR("❌ 改行が見つかりません"))
                self.stdout.write("   → PEM形式には改行が必要です\n")

            # クォートのチェック
            if secret.startswith('"') or secret.startswith("'"):
                self.stdout.write(self.style.WARNING("⚠️  先頭にクォートがあります"))
                self.stdout.write(
                    "   → .env ファイルではクォートは不要な場合があります\n"
                )

            # 正しい形式の例を表示
            self.stdout.write(self.style.WARNING("正しい .env の設定例:"))
            self.stdout.write("\nパターン1（1行形式、推奨）:")
            self.stdout.write(
                'SUPABASE_JWT_SECRET="-----BEGIN PUBLIC KEY-----\\nMFkw...\\n-----END PUBLIC KEY-----"\n'
            )

            self.stdout.write("\nパターン2（複数行形式）:")
            self.stdout.write('SUPABASE_JWT_SECRET="-----BEGIN PUBLIC KEY-----')
            self.stdout.write("MFkw...")
            self.stdout.write('-----END PUBLIC KEY-----"\n')

            # 処理後の形式を表示
            processed = secret
            if "\\n" in processed:
                processed = processed.replace("\\n", "\n")
            processed = processed.strip('"').strip("'")

            self.stdout.write(self.style.WARNING("\n処理後の公開鍵:"))
            self.stdout.write("─" * 60)
            self.stdout.write(processed)
            self.stdout.write("─" * 60)

        else:
            self.stdout.write(
                self.style.SUCCESS("✅ 通常の秘密鍵のようです (HS256用)\n")
            )
            self.stdout.write(f"秘密鍵: {secret[:20]}...\n")
