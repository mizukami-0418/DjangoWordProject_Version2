# contact/serializers.py

from rest_framework import serializers
from .models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    """お問い合わせのシリアライザー"""

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Inquiry
        fields = ["id", "subject", "context", "created_at", "user_email"]
        read_only_fields = ["id", "created_at", "user_email"]

    def validate_subject(self, value):
        """件名のバリデーション"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("件名は3文字以上で入力してください")
        return value.strip()

    def validate_context(self, value):
        """問い合わせ内容のバリデーション"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "お問い合わせ内容は10文字以上で入力してください"
            )
        if len(value.strip()) > 500:
            raise serializers.ValidationError(
                "お問い合わせ内容は500文字以内で入力してください"
            )
        return value.strip()


class InquiryCreateSerializer(serializers.Serializer):
    """お問い合わせ作成用のシリアライザー"""

    subject = serializers.CharField(
        max_length=50, min_length=3, help_text="件名（3〜50文字）"
    )
    context = serializers.CharField(
        max_length=500, min_length=10, help_text="お問い合わせ内容（10〜500文字）"
    )
