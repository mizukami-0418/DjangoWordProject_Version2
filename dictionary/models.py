from django.db import models

# 品詞モデル
class PartOfSpeech(models.Model):
    name = models.CharField(max_length=50, verbose_name='品詞') # 名詞、動詞など
    
    class Meta:
        db_table = 'part_of_speech'
        verbose_name_plural = '品詞'
    
    @property
    def part_of_speech_count(self):
        return self.part_of_speech.count()
    
    def __str__(self):
        return self.name

# 難易度モデル
class Level(models.Model):
    name = models.CharField(max_length=50, verbose_name='難易度') # 初級、中級など
    description = models.CharField(max_length=255,null=True, verbose_name='説明') # 難易度の説明
    
    class Meta:
        db_table = 'level'
        verbose_name_plural = '難易度'
    
    @property
    def level_count(self):
        return self.level.count()
    
    def __str__(self):
        return self.name

# 単語モデル
class Word(models.Model):
    english = models.CharField(max_length=255, verbose_name='英語', db_index=True, unique=True) # 英語
    japanese = models.CharField(max_length=255, verbose_name='日本語', db_index=True) # 日本語
    part_of_speech = models.ForeignKey(PartOfSpeech, on_delete=models.CASCADE, verbose_name='品詞', related_name='part_of_speech') # 品詞
    phrase = models.TextField(blank=True, null=True, verbose_name='成句') # 成句や例文
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name='難易度', related_name='level') # 難易度
    
    class Meta:
        db_table = 'word'
        verbose_name_plural = '単語'
    
    def __str__(self):
        return self.english