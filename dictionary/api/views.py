# dictionary/api/views.py
from rest_framework.viewsets import ModelViewSet
from dictionary.models import Word
from .serializers import WordSerializer


class WordViewSet(ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
