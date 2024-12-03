from django.contrib import admin
from .models import PartOfSpeech, Level, Word

# 品詞
class PartOfSpeechAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_of_speech_count_display')
    list_filter = ('name',)
    
    def part_of_speech_count_display(self, obj):
        return obj.part_of_speech_count
    part_of_speech_count_display.short_description = '登録数'

# 難易度
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'level_count_display')
    list_filter = ('name',)
    
    def level_count_display(self, obj):
        return obj.level_count
    level_count_display.short_description = '登録数'

# 単語
class WordAdmin(admin.ModelAdmin):
    list_display = ('english', 'japanese', 'part_of_speech', 'phrase', 'level')
    list_filter = ('part_of_speech', 'level',)
    
    fieldsets = (
        ('language', {'fields': ('english', 'japanese')}),
        ('description', {'fields': ('part_of_speech', 'phrase', 'level')}),
    )
    
    search_fields = ('english', 'japanese',)


admin.site.register(PartOfSpeech, PartOfSpeechAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Word, WordAdmin)