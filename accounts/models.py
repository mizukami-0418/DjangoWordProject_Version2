from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("メールアドレスを入力")
        if not username:
            raise ValueError("ユーザー名を入力")
        if not password:
            raise ValueError("パスワードを入力してください")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # ===== 🆕 Supabase連携用フィールド =====
    supabase_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Supabase ユーザーID",
        help_text="Supabase認証を使用する場合のユーザーID",
    )
    # =====================================

    email = models.EmailField(
        max_length=255, unique=True, verbose_name="メールアドレス"
    )
    username = models.CharField(max_length=50, verbose_name="ユーザー名")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "custom_user"
        verbose_name_plural = "ユーザー"

    def __str__(self):
        return self.email
