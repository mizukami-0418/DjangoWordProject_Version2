# dictionary/api/views.py
from rest_framework.viewsets import ModelViewSet
from dictionary.models import Word
from .serializers import WordSerializer


class WordViewSet(ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer

    def get_queryset(self):
        return Word.objects.all()  # After filtering on user_id

    # TODO: filter by supabase user_id
