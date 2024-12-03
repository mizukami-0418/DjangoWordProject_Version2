from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserEditForm, CustomPasswordChangeForm, CustomSetPasswordForm, CustomPasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from dictionary.models import Word
from flashcard.models import UserWordStatus
from accounts.models import CustomUser

# ユーザー新規登録
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
            return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# ログイン関数
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
                return redirect('login')
        else:
            messages.error(request, '入力に誤りがあります')
            return redirect('login')
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
    # レベルとモードのリストを定義
    levels = ['1', '2', '3', '4']
    modes = ['en', 'ja']
    
    # 各難易度の問題総数を取得
    total_counts = {
        level: Word.objects.filter(level=level).count()
        for level in levels
    }
    
    # ユーザーの回答実績を取得
    words_status = UserWordStatus.objects.filter(user=request.user)
    
    # 各難易度のモードごとの回答数と正解数を取得
    results = {
        level: {
            mode: {
                'count': words_status.filter(word__level=level, mode=mode).count(),
                'correct': words_status.filter(word__level=level, mode=mode, is_correct=True).count()
            }
            for mode in modes
        }
        for level in levels
    }
    
    # コンテキストを準備
    context = {
        'total_counts': total_counts,
        'results': results,
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
            return redirect('edit')
    else:
        form = UserEditForm(instance=request.user)
        
    return render(request, 'accounts/user_edit.html', {'form': form})

# ユーザー情報でパスワードを変更するクラス
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

# ユーザー情報でパスワード変更後にレンダリング
@login_required
def password_change_done(request):
    messages.success(request, 'パスワードが正常に変更されました')
    return render(request, 'accounts/password_change_done.html')


# パスワードを忘れた時のパスワードリセットクラス
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    
    # メールアドレスがユーザー登録されているか確認する関数
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        
        if email:
            if not CustomUser.objects.filter(email=email).exists():
                messages.error(self.request, "指定されたメールアドレスは登録されていません。")
                return redirect('password_reset')  # ログイン画面にリダイレクト
        return super().post(request, *args, **kwargs)

# パスワードリセット後のリンク先でパスワードを登録するクラス
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

