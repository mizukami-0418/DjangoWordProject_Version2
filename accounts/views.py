from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserEditForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy


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
    return render(request, 'accounts/user_detail.html')

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


@login_required
def password_change_done(request):
    messages.success(request, 'パスワードが正常に変更されました')
    return render(request, 'accounts/password_change_done.html')