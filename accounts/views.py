from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserEditForm, CustomPasswordChangeForm, CustomSetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.urls import reverse_lazy
from dictionary.models import Word
from flashcard.models import UserWordStatus


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, '新規登録しました')
            return redirect('user_home')
        else:
            messages.error(request, '登録失敗')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'ログインしました')
                return redirect('user_home')
            else:
                messages.error(request, 'ユーザーが存在しません')
        else:
            messages.error(request, '入力に誤りがあります')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

# ログアウト
@login_required
def user_logout(request):
    logout(request)
    request.session.flush() # セッションを完全に削除
    messages.success(request,'ログアウトしました')
    return redirect('home')

# ユーザー用ホーム画面
@login_required
def user_home(request):
    return render(request, 'accounts/user_home.html')

# ユーザー詳細画面
@login_required
def user_detail(request):
    # 各難易度の問題総数を算出
    beginner_all_counts = Word.objects.filter(level='1').count()
    intermediate_all_counts = Word.objects.filter(level='2').count()
    advanced_all_counts = Word.objects.filter(level='3').count()
    expert_all_counts = Word.objects.filter(level='4').count()
    # ユーザーの回答実績を取得
    words_status = UserWordStatus.objects.filter(user=request.user)
    
    # beginnerの回答数と正解数をモードごとに取得
    beginner_count_en = words_status.filter(word__level='1', mode='en').count()
    beginner_count_ja = words_status.filter(word__level='1', mode='ja').count()
    beginner_correct_en = words_status.filter(word__level='1', mode='en', is_correct=True).count()
    beginner_correct_ja = words_status.filter(word__level='1', mode='ja', is_correct=True).count()
    
    # intermediate
    intermediate_count_en = words_status.filter(word__level='2', mode='en').count()
    intermediate_count_ja = words_status.filter(word__level='2', mode='ja').count()
    intermediate_correct_en = words_status.filter(word__level='2', mode='en', is_correct=True).count()
    intermediate_correct_ja = words_status.filter(word__level='2', mode='ja', is_correct=True).count()
    
    # advanced
    advanced_count_en = words_status.filter(word__level='3', mode='en').count()
    advanced_count_ja = words_status.filter(word__level='3', mode='ja').count()
    advanced_correct_en = words_status.filter(word__level='3', mode='en', is_correct=True).count()
    advanced_correct_ja = words_status.filter(word__level='3', mode='ja', is_correct=True).count()
    
    # expert
    expert_count_en = words_status.filter(word__level='4', mode='en').count()
    expert_count_ja = words_status.filter(word__level='4', mode='ja').count()
    expert_correct_en = words_status.filter(word__level='4', mode='en', is_correct=True).count()
    expert_correct_ja = words_status.filter(word__level='4', mode='ja', is_correct=True).count()
    
    context = {
        'beginner_all_counts': beginner_all_counts,
        'intermediate_all_counts': intermediate_all_counts,
        'advanced_all_counts': advanced_all_counts,
        'expert_all_counts': expert_all_counts,
        'beginner_count_en': beginner_count_en,
        'beginner_count_ja': beginner_count_ja,
        'beginner_correct_en': beginner_correct_en,
        'beginner_correct_ja': beginner_correct_ja,
        'intermediate_count_en': intermediate_count_en,
        'intermediate_count_ja': intermediate_count_ja,
        'intermediate_correct_en': intermediate_correct_en,
        'intermediate_correct_ja': intermediate_correct_ja,
        'advanced_count_en': advanced_count_en,
        'advanced_count_ja': advanced_count_ja,
        'advanced_correct_en': advanced_correct_en,
        'advanced_correct_ja': advanced_correct_ja,
        'expert_count_en': expert_count_en,
        'expert_count_ja': expert_count_ja,
        'expert_correct_en': expert_correct_en,
        'expert_correct_ja': expert_correct_ja,
    }
    
    return render(request, 'accounts/user_detail.html', context)

# ユーザー編集
@login_required
def user_edit(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'ユーザー情報を更新しました')
            return redirect('detail')
        else:
            messages.error(request, '更新に失敗しました。再入力お願いします')
    else:
        form = UserEditForm(instance=request.user)
        
    return render(request, 'accounts/user_edit.html', {'form': form})

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('password_change_done')
    
    def form_invalid(self, form):
        # 各フィールドのエラーメッセージを取得し、messages.errorに追加
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form.fields[field].label}: {error}")
        return super().form_invalid(form)
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_invalid(self, form):
        # 各フィールドのエラーメッセージを取得し、messages.errorに追加
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form.fields[field].label}: {error}")
        return super().form_invalid(form)


@login_required
def password_change_done(request):
    messages.success(request, 'パスワードが正常に変更されました')
    return render(request, 'accounts/password_change_done.html')