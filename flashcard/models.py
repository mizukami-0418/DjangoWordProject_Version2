from django.db import models
from accounts.models import CustomUser
from dictionary.models import Word
from dictionary.models import Level


# 通常モードとテストモードの進行状況
class UserProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) # ユーザー
    level = models.ForeignKey(Level, on_delete=models.CASCADE) # 対象のレベル
    mode = models.CharField(max_length=10) # モード
    score = models.IntegerField(default=0) # スコア（正解数）
    total_questions = models.IntegerField(default=0) # 問題数のトータル
    current_question_index = models.IntegerField(default=0) # 現在の問題インデックス
    question_ids = models.TextField(blank=0, null=True) # 出題された問題のIDリストをシリアライズして保存
    completed_at = models.DateTimeField(auto_now_add=True) # 完了日時
    is_completed = models.BooleanField(default=False) # 完了しているかどうか
    is_paused = models.BooleanField(default=False) # 中断データがあるか
    
    class Meta:
        db_table = 'user_progress'
        verbose_name = 'ユーザー進行状況'
        verbose_name_plural = 'ユーザー進行状況'
    
    def __str__(self):
        return self.user.username
        # return f"{self.user.username} - {self.level.name} - {self.mode}: {self.score}/{self.total_questions}"


# 単語ごとの正誤履歴
class UserWordStatus(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # ユーザー
    word = models.ForeignKey(Word, on_delete=models.CASCADE)  # 問題（単語）
    is_correct = models.BooleanField(default=False)  # 正誤データ
    mode = models.CharField(max_length=10)  # モード（英訳か和訳か）
    last_attempted_at = models.DateTimeField(auto_now=True)  # 最後に回答した日時

    class Meta:
        unique_together = ('user', 'word', 'mode')  # ユーザー、単語、モードの組み合わせを一意にする
        db_table = 'user_word_status'
        verbose_name = '正解ステータス情報'
        verbose_name_plural = '正解ステータス情報'


# 復習モードの進行状況
class UserReviewProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # ユーザー
    questions = models.ManyToManyField(Word)  # 復習対象の問題（複数問題を持つ）
    mode = models.CharField(max_length=10) # モード
    current_question_index = models.IntegerField(default=0)  # 現在の問題インデックス
    total_questions = models.IntegerField(default=0)  # 総問題数
    score = models.IntegerField(default=0)  # 正解数
    is_completed = models.BooleanField(default=False)  # 復習が完了したかどうか
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    is_paused = models.BooleanField(default=False) # 中断データがあるか
    
    class Meta:
        db_table = 'review_progress'
        verbose_name = '復習進行状況'
        verbose_name_plural = '復習進行状況'
        
    def __str__(self):
        return self.user.username


'''
class AnswerHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 回答者
    question = models.ForeignKey(Word, on_delete=models.CASCADE)  # 問題（単語）
    is_correct = models.BooleanField(default=False)  # 正誤の記録
    mode = models.CharField(max_length=10)  # モード (例: 'en', 'jp')
    answered_at = models.DateTimeField(auto_now_add=True)  # 回答日時
    
    class Meta:
        db_table = 'answer_history'
        verbose_name = '回答履歴'
        verbose_name_plural = '回答履歴'

    def __str__(self):
        return f"{self.user.username} - {self.question.english} - Mode: {self.mode} - {'正解！' if self.is_correct else '不正解'}"
'''