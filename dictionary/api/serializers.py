# dictionary/api/serializers.py
from rest_framework import serializers
from dictionary.models import Word


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = "__all__"
