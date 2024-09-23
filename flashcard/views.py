from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from dictionary.models import Word, Level
from django.http import Http404, HttpResponse
from django.contrib import messages
from .models import UserProgress, UserWordStatus, UserReviewProgress
import random
import json

# 「最初から」か「続きから」を選択する
@login_required
def select_quiz(request):
    user_progress = UserProgress.objects.filter(user=request.user,is_completed=False).first()
    review_progress = UserReviewProgress.objects.filter(user=request.user, is_completed=False).first()
    user_word_status = UserWordStatus.objects.filter(user=request.user, is_correct=False).first()
    
    # POSTリクエスト
    if request.method == 'POST':
        # POStリクエストからquiz_mode(newかcontinue)を取得
        selection = request.POST.get('quiz_mode')
        
        # 「最初から」を選んだ場合、新しくクイズを開始する
        if selection == 'new':
            return redirect('select_level')
        
        # 「前回の続きから」はuser_progress.idからデータを取得し、再開する
        elif selection == 'continue':
            user_progress_data = UserProgress.objects.filter(user=request.user, is_completed=False).all()
            return render(request, 'flashcard/show_paused_data.html', {'user_progress_data': user_progress_data})
        # 復習モードの続き
        elif selection == 'review_continue':
            review_progress_data = UserReviewProgress.objects.filter(user=request.user, is_completed=False).all()
            return render(request, 'flashcard/show_review_paused_data.html', {'review_progress_data': review_progress_data})
        # 復習モード
        elif selection == 'review':
            return render(request, 'flashcard/review_select_mode.html')
        # リプレイモード
        elif selection == 'replay':
            request.session['replay'] = 'replay'
            return redirect('select_level')
        # テストモード
        elif selection == 'test':
            request.session['test'] = 'test'
            return redirect('select_level')
        
        # quiz_modeを取得できないか、上記以外の場合はuser_homeへ
        else:
            messages.error(request, 'エラーが発生しました。最初からお願いします。')
            return redirect('user_home')
    
    # GETリクエストの場合、contextに進行状況と正誤データを渡し、select_quiz.htmlにレンダリング
    context = {
        'user_progress': user_progress,
        'review_progress': review_progress,
        'user_word_status': user_word_status,
    }
    return render(request, 'flashcard/select_quiz.html', context)


# 難易度セレクト
@login_required
def select_level(request):
    if request.method == 'POST':
        level_id = request.POST.get('level')
        # セッションにlevel_idを保存し、select_modeにリダイレクト
        request.session['level_id'] = level_id
        return redirect('select_mode')
    else:
        # データベースから取得した全てのLevelオブジェクトを渡し、select_level.htmlをレンダリング
        levels = Level.objects.all()
    return render(request, 'flashcard/select_level.html', {'levels': levels})


# セッションデータ取得用ヘルパー関数
def get_quiz_session_data(request):
    # セッションから難易度、モード、問題数を取得して返す
    level_id = request.session.get('level_id')
    mode = request.session.get('mode')
    # num_questions = request.session.get('num_questions')
    
    level = get_object_or_404(Level, id=level_id)
    
    return level, mode


# モードセレクト
@login_required
def select_mode(request):
    # ヘルパー関数を使用し、levelを取得
    level, _= get_quiz_session_data(request)
    # 入力確認
    if level is None:
        messages.error(request, 'エラーが発生しました。最初からお願いします')
        return redirect('select_level')
    
    # POSTリクエスト
    if request.method == 'POST':
        # ポストデータからモードを取得し、セッションに保持。select_num_questionsにリダイレクト
        mode = request.POST.get('mode')
        request.session['mode'] = mode
        return redirect('quiz')
    
    # GETリクエスト
    # 取得したlevelを渡し、select_mode.htmlをレンダリング
    return render(request, 'flashcard/select_mode.html', {'level': level})


# 単語帳クイズの初期設定を行う関数
@login_required
def quiz(request):
    # テストモードとリプレイモードの場合、セッション情報を取得しセッションデータを削除
    test = request.session.pop('test', None)
    replay = request.session.pop('replay', None)
    # ヘルパー関数を使用し、各データを取得
    level, mode = get_quiz_session_data(request)
    # データが全て存在しない場合
    if not (level and mode):
        messages.error(request, 'エラーが発生しました。難易度選択からお願いします')
        return redirect('select_level')
    
    words = Word.objects.filter(level_id=level.id) # 選択した難易度の単語を全て抽出
    # 抽出した単語が選択した出題数より少ない場合、エラーにならないための処理
    
    # テストモードの場合、ランダムで5問出題する
    if test: 
        total_questions = 5
        questions = random.sample(list(words.values_list('id', flat=True)), total_questions)
        messages.success(request, 'テストモードに来た')
    elif replay:
        # UserWordStatusから選択したモードの単語を全て取得
        replay_all_questions = UserWordStatus.objects.filter(user=request.user, mode=mode)
        print(len(replay_all_questions))
        # そこから単語のidを取得
        replay_all_questions_id = replay_all_questions.values_list('word_id', flat=True)
        print(replay_all_questions_id)
        # 選択したlevelでフィルタリングされたwordsからreplay_all_questions_idの単語を取得
        replay_questions = words.filter(id__in=replay_all_questions_id)
        print(replay_questions)
        total_questions = len(replay_questions)
        print(total_questions)
        questions = random.sample(list(replay_questions.values_list('id', flat=True)), total_questions)
        print(questions)
        if questions:
            messages.success(request, 'リプレイに来た')
            pass
        else:
            messages.success(request, '初めての挑戦です。「最初から」モードで開始してください')
            return redirect('user_home')
    # 通常モードの場合
    else:
        total_questions = len(words)
        # total_questionsの数だけ、wordsからidで取得し、questionsにリストで保存
        questions = random.sample(list(words.values_list('id', flat=True)), total_questions)
        messages.success(request, '通常モードに来た')
        # question_indexとscoreを初期化
        
    question_index = 0
    score = 0
    
    # 途中経過保存用UserProgressモデルを作成
    user_progress = UserProgress.objects.create(
        user=request.user,
        level=level,
        mode=mode,
        score=score,
        total_questions=total_questions,
        current_question_index=question_index,
        question_ids=json.dumps(questions),
    )
    # questionsリストから、現在の問題のIDをquestion_indexを使って取得
    question_id = questions[question_index]
    # Wordモデルからquestion_idで問題を取得
    current_question = Word.objects.get(id=question_id)
    
    # contextに現在の問題と進行状況を渡し、quiz.htmlにレンダリング
    context = {
        'current_question': current_question,
        'user_progress': user_progress,
    }
    return render(request, 'flashcard/quiz.html', context)


# 現在の問題を取得するヘルパー関数
def get_current_question(request, progress_id):
    # 進行状況とWordから現在の問題を取得し返す
    user_progress = get_object_or_404(UserProgress, id=progress_id, user=request.user, is_completed=False)
    questions = json.loads(user_progress.question_ids)
    question_id = questions[user_progress.current_question_index]
    current_question = get_object_or_404(Word, id=question_id)
    
    return user_progress, current_question

# 中断データで再開
@login_required
def quiz_restart(request, progress_id):
    # get_current_questionで進捗状況と現在の問題を取得
    user_progress, current_question = get_current_question(request, progress_id)
    
    # user_progressと　current_questionの両方が存在しない場合
    if not(user_progress and current_question):
        messages.error(request, '問題がありませんでした。ホーム画面へ戻ります')
        return redirect('user_home')
    
    # contextに現在の問題と進行状況を渡し、quiz.htmlにレンダリング
    context = {
        'current_question': current_question,
        'user_progress': user_progress,        
    }
    return render(request, 'flashcard/quiz.html', context)

# 復習モード
@login_required
def start_review(request):
    if request.method == 'POST':
        mode = request.POST.get('mode')
        # modeが存在しない場合はuser_homeへリダイレクト
        if mode is None:
            messages.error(request, 'モードを取得できませんでした。ホームへ戻ります')
            return redirect('user_home')
        
        # 特定のモードに基づいて、ユーザーが間違った問題を取得
        mistakes = UserWordStatus.objects.filter(user=request.user, mode=mode, is_correct=False)
        # mistakesが存在する場合はreview_quizにリダイレクト
        if mistakes:
            # mistakesから各mistake.wordを取得し、questionsリストを作成
            questions = [mistake.word for mistake in mistakes]
            # 復習進行状況を作成
            review_progress = UserReviewProgress.objects.create(
                user = request.user,
                mode = mode,
                total_questions = len(questions),
            )
            # review_progressのquestionsフィールドにquestionsリストを関連付ける（既存の関連はクリアされる）
            review_progress.questions.set(questions)
            
            return redirect('review_quiz', review_id=review_progress.id)
        # mistakesがなかった場合はuser_homeへ
        else:
            messages.error(request, '間違った問題はありませんでした')
            return redirect('user_home')
    # POSTメソッド以外のリクエストはuser_homeへ
    else:
        messages.error(request, 'ページに辿り着けませんでした')
        return redirect('user_home')

# 復習モードを開始
@login_required
def review_quiz(request, review_id):
    if review_id is None: # review_idが存在しない場合
        messages.error(request, 'エラーが発生しました。最初からお願いします')
        return redirect('user_home')
    # 復習の進行状況を取得
    review_progress = get_object_or_404(UserReviewProgress, id=review_id, user=request.user,)
    # 現在問題番号から最初の問題を取得
    current_question = review_progress.questions.all()[review_progress.current_question_index]
    
    # contextに最初の問題と進行状況を渡し、review_quiz.htmlにレンダリング
    context = {
        'current_question': current_question,
        'review_progress': review_progress,
    }
    return render(request, 'flashcard/review_quiz.html', context)


# 復習モードの回答の正誤を判定する関数
@login_required
def check_review_answer(request, progress_id):
    if progress_id is None: # progress_idが存在しない場合
        messages.error(request, 'エラーが発生しました。一度ホームへ戻ります')
        return redirect('user_home')
    # 復習の進行状況を取得
    review_progress = get_object_or_404(UserReviewProgress, id=progress_id, user=request.user,)
    # 現在の問題を取得
    current_question = review_progress.questions.all()[review_progress.current_question_index]
    # ポストデータからanswerを取得
    answer = request.POST.get('answer').strip().lower()
    # 問題の解答を取得
    correct_answer = current_question.english if review_progress.mode == 'en' else current_question.japanese.split(',')
    # is_correctをFalseに設定
    is_correct = False
    
    if request.method == 'POST':
        # 英訳モード
        if review_progress.mode == 'en':
            if answer == correct_answer:
                messages.success(request, '正解！！！！')
                review_progress.score += 1 # 正解数を１加算
                is_correct = True # 正誤記録を更新
            else:
                messages.error(request, '残念')
        # 和訳モード
        else:
            # answerがcorrect_answerリストのいずれかの要素（日本語の正解）と一致するかを確認
            if any(answer == correct_answer_japanese.strip() for correct_answer_japanese in correct_answer):
                messages.success(request, '正解！！！！')
                review_progress.score += 1 # 正解数を１加算
                is_correct = True # 正誤記録を更新
            else:
                messages.error(request, '残念')

        # UserWordStatusの更新または作成（ユーザーごとの正解状態とモードを保存）
        user_word_status, created = UserWordStatus.objects.get_or_create(
            user=request.user,
            word=current_question,
            mode=review_progress.mode  # モードを追加
        )
        user_word_status.is_correct = is_correct
        user_word_status.save()
        
        review_progress.current_question_index += 1 # 問題番号を1加算
        review_progress.save()
        
        # 問題数の確認
        # current_question_indexが総出題数以上
        if review_progress.current_question_index >= review_progress.total_questions:
            review_progress.is_completed = True
            review_progress.is_paused = False
            review_progress.save()
            return render(request, 'flashcard/last_check_review_answer.html', {'review_progress':review_progress, 'current_question': current_question})
        else:
            review_progress.save()
            return render(request, 'flashcard/check_review_answer.html', {'review_progress': review_progress, 'current_question': current_question})
    
    # POSTリクエスト以外はホームへリダイレクト
    else:
        messages.error(request, 'ページに辿り着けませんでした')
        return redirect('user_home')


# 回答の正誤を判定する関数
@login_required
def check_answer(request, progress_id):
    # get_current_questionで進捗状況と現在の問題を取得
    user_progress, current_question = get_current_question(request, progress_id)
    answer = request.POST.get('answer').strip().lower() #POSTリクエストからanswerを取得
    # 問題の解答を取得
    correct_answer = current_question.english if user_progress.mode == 'en' else current_question.japanese.split(',')
        
    if request.method == 'POST':
        is_correct = False # 正誤記録を初期化
        # 英訳モード
        if user_progress.mode == 'en':
            if answer == correct_answer:
                messages.success(request, '正解！！！！')
                user_progress.score += 1 # 正解数を１加算
                is_correct = True # 正誤記録を更新
            else:
                messages.error(request, '残念')
        else: # 和訳モード
            if any(answer == correct_answer_japanese.strip() for correct_answer_japanese in correct_answer):
                messages.success(request, '正解！！！！')
                user_progress.score += 1 # 正解数を１加算
                is_correct = True # 正誤記録を更新
            else:
                messages.error(request, '残念')
        
        # UserWordStatusの更新または作成（ユーザーごとの正解状態とモードを保存）
        user_word_status, created = UserWordStatus.objects.get_or_create(
            user=request.user,
            word=current_question,
            mode=user_progress.mode  # モードを追加
        )
        user_word_status.is_correct = is_correct
        user_word_status.save()
        
        user_progress.current_question_index += 1 # 問題番号を1加算
        
        # 問題数の確認
        # current_question_indexが総出題数以上
        if user_progress.current_question_index >= user_progress.total_questions:
            user_progress.is_completed = True
            user_progress.is_paused = False
            user_progress.save()
            return render(request, 'flashcard/last_check_answer.html', {'user_progress':user_progress, 'current_question': current_question})
        else:
            user_progress.save()
            return render(request, 'flashcard/check_answer.html', {'user_progress': user_progress, 'current_question': current_question})
    
    # POSTリクエスト以外はuser_homeにリダイレクト
    else:
        messages.error(request, 'ページに辿り着けませんでした')
        return redirect('user_home')

# 単語帳モード中断用関数
@login_required
def pause_quiz(request, progress_id):
    user_progress = get_object_or_404(UserProgress, id=progress_id, user=request.user)
    if user_progress is None: # 進行状況が存在しない場合
        messages.error(request, 'エラーが発生しました。ホームへ戻ります')
        return redirect('user_home')
    
    if not user_progress.is_completed: # 問題が完了していない場合
        # user_progressを保存する
        user_progress.is_paused = True
        user_progress.save()
        
        messages.success(request, '途中経過を保存しました')
        return redirect('user_home')
    
    else: # 完了していた場合
        messages.success(request, 'エラーが発生しました。ホームへ戻ります')
        return redirect('user_home')

# 復習モード中断用関数
@login_required
def pause_review(request, progress_id):
    review_progress = get_object_or_404(UserReviewProgress, id=progress_id, user=request.user)
    if review_progress is None: # review_progressが存在しない場合
        messages.error(request, 'エラーが発生しました。ホームへ戻ります')
        return redirect('user_home')
    
    if not review_progress.is_completed: # 問題が完了していない場合
        # review_progressを保存する
        review_progress.is_paused = True
        review_progress.save()
        messages.success(request, '途中経過を保存しました')
        return redirect('user_home')
    
    else: # 完了していた場合
        messages.error(request, 'エラーが発生しました。ホームへ戻ります。')
        return redirect('user_home')

# 中断データを削除関数
def reset_user_progress(request, progress_id):
    user_progress = get_object_or_404(UserProgress, id=progress_id, user=request.user)
    user_progress.is_completed = True
    user_progress.is_paused = False
    user_progress.save()
    messages.success(request, '中断データをリセットしました')
    return redirect('user_home')


def reset_review_progress(request, progress_id):
    review_progress = get_object_or_404(UserReviewProgress, id=progress_id, user=request.user)
    review_progress.is_completed = True
    review_progress.is_paused = False
    review_progress.save()
    messages.success(request, '中断データをリセットしました')
    return redirect('user_home')



# 単語帳モードの最終結果を表示する関数
@login_required
def result(request, progress_id):
    if progress_id is None: # progress_idが存在しない場合
        messages.error(request, 'エラーが発生しました。ホームへ戻ります。')
        return redirect('user_home')
    
    user_progress = get_object_or_404(UserProgress, id=progress_id)
    # 正答率
    correct_answer_rate = int( user_progress.score / user_progress.total_questions * 100)
    
    # contextに正答率と進行状況を渡し、result.htmlにレンダリング
    context = {
        'correct_answer_rate':correct_answer_rate,
        'user_progress': user_progress,
    }
    # テストモードの場合
    if user_progress.total_questions == 5:
        return render(request, 'flashcard/test_result.html', context)
    
    return render(request, 'flashcard/result.html', context)

# 復習モードの最終結果を表示する関数
@login_required
def review_result(request, progress_id):
    if progress_id is None: # progress_idが存在しない場合
        messages.error(request, 'エラーが発生しました。ホームへ戻ります。')
        return redirect('user_home')
    
    review_progress = get_object_or_404(UserReviewProgress, id=progress_id)
    # 正答率
    correct_answer_rate = int(review_progress.score / review_progress.total_questions * 100 )
    
    # contextに正答率と復習モード進行状況を渡し、result.htmlにレンダリング
    context = {
        'correct_answer_rate':correct_answer_rate,
        'review_progress': review_progress,
    }
    return render(request, 'flashcard/review_result.html', context)


'''
2024/9/16 コードはオッケー。UI変更のため一旦コメントアウトし保存
# 問題数セレクト
def select_num_questions(request):
    # ヘルパー関数で難易度とモードを取得
    level, mode, _ = get_quiz_session_data(request)
    if not(level and mode):
        messages.error(request, 'エラーが発生しました。再度選択してください')
        return redirect('select_level')
    
    # POSTリクエスト
    if request.method == 'POST':
        # ポストデータの問題数を取得
        num_questions = request.POST.get('num_questions')
        # num_questionsのバリデーション
        if num_questions is None or not num_questions.isdigit() or int(num_questions) <= 0:
            messages.error(request, 'エラーが発生しました。再度問題数を選択してください')
            # もう一度問題数セレクトを表示
            return render(request, 'flashcard/select_num_questions.html', {'level': level, 'mode': mode})
        # 正常な場合は、セッションに保存しリダイレクト
        request.session['num_questions'] = int(num_questions)
        return redirect('select_quiz')
    
    # GETリクエスト
    return render(request, 'flashcard/select_num_questions.html', {'level': level, 'mode': mode})


# 「最初から」か「続きから」を選択する
def select_quiz(request):
    # ヘルパー関数を使用し、level他を取得
    level, mode, num_questions = get_quiz_session_data(request)
    if not (level and mode and num_questions):
        messages.error(request, 'エラーが発生しました。最初からお願いします')
        return redirect('select_level')
    
    user_progress = UserProgress.objects.filter(user=request.user, level=level, mode=mode, total_questions=num_questions, is_completed=False).first()
    
    # POSTリクエスト
    if request.method == 'POST':
        # POStリクエストからquiz_mode(newかcontinue)を取得
        selection = request.POST.get('quiz_mode')
        
        # 「最初から」を選んだ場合、新しくクイズを開始する
        if selection == 'new':
            return redirect('quiz')
        # 「前回の続きから」はuser_progress.idからデータを取得し、再開する
        elif selection == 'continue':
            user_progress_data = UserProgress.objects.filter(user=request.user, level=level, mode=mode, total_questions=num_questions, is_completed=False).all()
            return render(request, 'flashcard/show_paused_data.html', {'user_progress_data': user_progress_data})
            # return redirect('quiz_restart', progress_id=user_progress.id)
        else:
            messages.error(request, 'エラーが発生しました。最初からお願いします。')
            return redirect('select_level')
    # GETリクエストの場合は、フォームを表示する
    context = {
        'level': level,
        'mode': mode,
        'num_questions': num_questions,
        'user_progress': user_progress,
    }
    return render(request, 'flashcard/select_quiz.html', context)
'''

'''
# 問題数セレクト
@login_required
def select_num_questions(request):
    # ヘルパー関数で難易度とモードを取得
    level, mode, _ = get_quiz_session_data(request)
    # 入力確認。難易度とモードがない場合
    if not(level and mode):
        messages.error(request, 'エラーが発生しました。再度選択してください')
        return redirect('select_level')
    
    # POSTリクエスト
    if request.method == 'POST':
        # ポストデータの問題数を取得
        num_questions = request.POST.get('num_questions')
        # num_questionsのバリデーション。num_questionsの存在。数値であるか。整数で0以上か。
        if num_questions is None or not num_questions.isdigit() or int(num_questions) <= 0:
            messages.error(request, 'エラーが発生しました。再度問題数を選択してください')
            # もう一度問題数セレクトを表示
            return render(request, 'flashcard/select_num_questions.html', {'level': level, 'mode': mode})
        # 正常な場合は、num_questionsを整数に変換し、セッションに保存しquizにリダイレクト
        request.session['num_questions'] = int(num_questions)
        return redirect('quiz')
    
    # GETリクエスト
    # levelとmodeを渡し、select_num_questions.htmlをレンダリング
    return render(request, 'flashcard/select_num_questions.html', {'level': level, 'mode': mode})
'''