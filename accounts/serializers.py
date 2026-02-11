# accounts/serializers.py

from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    ユーザー情報の基本シリアライザー
    読み取り専用フィールドが多い
    """
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'is_active', 'supabase_id']
        read_only_fields = ['id', 'email', 'supabase_id', 'is_active']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    ユーザープロフィール更新用シリアライザー
    usernameのみ更新可能
    """
    
    class Meta:
        model = CustomUser
        fields = ['username']
    
    def validate_username(self, value):
        """usernameのバリデーション"""
        if not value:
            raise serializers.ValidationError('ユーザー名を入力してください')
        
        if len(value) < 2:
            raise serializers.ValidationError('ユーザー名は2文字以上にしてください')
        
        if len(value) > 50:
            raise serializers.ValidationError('ユーザー名は50文字以内にしてください')
        
        return value


class CompleteProfileSerializer(serializers.Serializer):
    """
    初回登録時のusername設定用シリアライザー
    """
    username = serializers.CharField(
        max_length=50,
        min_length=2,
        required=True,
        error_messages={
            'required': 'ユーザー名を入力してください',
            'max_length': 'ユーザー名は50文字以内にしてください',
            'min_length': 'ユーザー名は2文字以上にしてください',
        }
    )
    
    def validate_username(self, value):
        """usernameのバリデーション"""
        # 既に使用されているusernameかチェック（オプション）
        # if CustomUser.objects.filter(username=value).exists():
        #     raise serializers.ValidationError('このユーザー名は既に使用されています')
        
        return value