from django.contrib import admin
from .models import UserProgress, UserWordStatus, UserReviewProgress

# 進捗情報管理
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_level', 'get_mode', 'get_score', 'is_completed', 'is_paused')
    list_filter = ('level', 'mode', 'is_completed', 'is_paused',)
    
    search_fields = ('user__username',)
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'ユーザー名'
    
    def get_level(self, obj):
        return obj.level
    get_level.short_description = '難易度'
    
    def get_mode(self, obj):
        return obj.mode
    get_mode.short_description = '選択モード'
    
    def get_score(self, obj):
        return obj.score
    get_score.short_description = 'スコア'
    

# 単語帳回答実績確認
class UserWordStatusAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_word_english', 'get_word_japanese', 'get_mode', 'is_correct')
    list_filter = ('mode', 'is_correct')
    
    search_fields = ('user__username', 'word__english', 'word__japanese',)
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'ユーザー名'
    
    def get_word_english(self, obj):
        return obj.word.english
    get_word_english.short_description = '英語'
    
    def get_word_japanese(self, obj):
        return obj.word.japanese
    get_word_japanese.short_description = '日本語'
    
    def get_mode(self, obj):
        return obj.mode
    get_mode.short_description = '選択モード'

# 復讐モードの進捗管理
class UserReviewProgressAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_mode', 'get_score', 'get_total_questions', 'is_completed', 'is_paused')
    list_filter = ('mode', 'is_completed', 'is_paused',)
    
    search_fields = ('user__username',)
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'ユーザー名'
    
    def get_mode(self, obj):
        return obj.mode
    get_mode.short_description = '選択モード'
    
    def get_score(self, obj):
        return obj.score
    get_score.short_description = 'スコア'
    
    def get_total_questions(self, obj):
        return obj.total_questions
    get_total_questions.short_description = '総出題数'

admin.site.register(UserProgress, UserProgressAdmin)
admin.site.register(UserWordStatus, UserWordStatusAdmin)
admin.site.register(UserReviewProgress, UserReviewProgressAdmin)

