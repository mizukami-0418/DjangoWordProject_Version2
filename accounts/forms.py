from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser

# 
class UserRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(label='確認用パスワード', widget=forms.PasswordInput(attrs={'placeholder': '確認用パスワード', 'class': 'form-control'}))
    
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'confirm_password']
        labels = {
            'email': 'メールアドレス',
            'username': 'ユーザー名',
            'password': 'パスワード',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'sample@example.com', 'class': 'form-control'}),
            'username': forms.TextInput(attrs={'placeholder': 'Yamada Taro', 'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'パスワード', 'class': 'form-control'}),
        }        
        
    def clean_confirm_password(self):
        cd = self.cleaned_data
        if cd['password'] != cd['confirm_password']:
            raise forms.ValidationError('パスワードが一致しません')
        return cd['confirm_password']


# カスタムパスワードリセットフォームの作成
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='メールアドレス', 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

# カスタムセットパスワードフォームの作成
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="新しいパスワード",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="新しいパスワード（確認）",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")
        try:
            validate_password(new_password1, self.user)
        except ValidationError as e:
            self.add_error('new_password1', e)
        return new_password1

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserEditForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        fields = ['email', 'username']
        labels = {
            'email': 'メールアドレス',
            'username': 'ユーザー名',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'sample@example.com', 'class': 'form-control'}),
            'username': forms.TextInput(attrs={'placeholder': 'Yamada Taro', 'class': 'form-control'}),
        }

# パスワード変更フォーム
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="現在のパスワード", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '現在のパスワードを入力'})
    )
    new_password1 = forms.CharField(
        label="新しいパスワード",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '新しいパスワードを入力'})
    )
    new_password2 = forms.CharField(
        label="新しいパスワード（確認）",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '新しいパスワードを再入力'})
    )
    
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")
        try:
            validate_password(new_password1, self.user)
        except ValidationError as e:
            self.add_error('new_password1', e)
        return new_password1


# 管理者権限でのユーザー作成用フォーム
class UserCreationForm(forms.ModelForm):
    username = forms.CharField(label='ユーザー名')
    email = forms.EmailField(label='メールアドレス')
    password1 = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    password2 = forms.CharField(label='パスワード確認', widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('パスワードが一致しません')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user