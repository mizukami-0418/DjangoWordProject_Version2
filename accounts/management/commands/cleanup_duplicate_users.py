# accounts/management/commands/cleanup_duplicate_users.py
# 重複したメールアドレスのユーザーをクリーンアップ

from django.core.management.base import BaseCommand
from django.db.models import Count
from accounts.models import CustomUser


class Command(BaseCommand):
    help = "重複したメールアドレスのユーザーをクリーンアップ"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="実際には削除せず、削除対象のみ表示",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(self.style.WARNING("\n=== 重複ユーザークリーンアップ ===\n"))

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN モード: 実際には削除しません\n")
            )

        # 重複したメールアドレスを持つユーザーを検索
        duplicates = (
            CustomUser.objects.values("email")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )

        if not duplicates:
            self.stdout.write(
                self.style.SUCCESS("✅ 重複するユーザーは見つかりませんでした")
            )
            return

        self.stdout.write(f"⚠️  重複するメールアドレス: {len(duplicates)}件\n")

        total_deleted = 0

        for dup in duplicates:
            email = dup["email"]
            users = CustomUser.objects.filter(email=email).order_by("id")

            self.stdout.write(f"\nメールアドレス: {email}")
            self.stdout.write(f"  ユーザー数: {users.count()}件")

            # 各ユーザーの情報を表示
            for i, user in enumerate(users):
                status = "✅ 保持" if i == 0 else "❌ 削除対象"
                self.stdout.write(
                    f"  {status} ID={user.id}, "
                    f"supabase_id={user.supabase_id or 'なし'}, "
                    f"username={user.username}, "
                    f"created={user.date_joined if hasattr(user, 'date_joined') else '不明'}"
                )

            # 最初のユーザー以外を削除
            if not dry_run:
                users_to_delete = users[1:]  # 2番目以降
                count = users_to_delete.count()
                users_to_delete.delete()
                total_deleted += count
                self.stdout.write(
                    self.style.SUCCESS(f"  → {count}件のユーザーを削除しました")
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n実際に削除する場合は --dry-run を外して実行してください"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ 合計 {total_deleted}件のユーザーを削除しました"
                )
            )

        # 残ったsupabase_idがないユーザーを確認
        users_without_supabase_id = CustomUser.objects.filter(supabase_id__isnull=True)
        if users_without_supabase_id.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  supabase_idが設定されていないユーザー: {users_without_supabase_id.count()}件"
                )
            )
            for user in users_without_supabase_id[:5]:  # 最初の5件のみ表示
                self.stdout.write(
                    f"  - ID={user.id}, email={user.email}, username={user.username}"
                )
