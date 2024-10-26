from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from .models import Word

# 単語検索機能
@login_required
def search(request):
    query = request.GET.get('query', '')  # 検索クエリを取得
    results = []
    
    if query:
        # 英語または日本語で検索
        results = Word.objects.filter(
            Q(english__iexact=query) | Q(japanese__icontains=query) # 英語は完全一致で、日本語は部分一致
        )
    else:
        return render(request, 'dictionary/search.html', {'results': results, 'query': query})
    
    return render(request, 'dictionary/search_result.html', {'results': results, 'query': query})
