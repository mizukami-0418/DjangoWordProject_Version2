# contact/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InquiryForm


@login_required
def contact_view(request):
    success_message = 'お問い合わせを受け付けました。\n登録メールアドレスへ5営業日以内にご連絡いたします。'
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)  # 一旦保存を延期
            inquiry.user = request.user  # ログインしているユーザーをセット
            inquiry.save()  # 保存
            messages.success(request, success_message)
            return redirect('contact_result')
        else:
            messages.error(request, '入力内容に誤りがあります。再度ご確認ください。')
            return render(request, 'contact/contact.html', {'form': form})
    else:
        form = InquiryForm()
    return render(request, 'contact/contact.html', {'form': form})

@login_required
def contact_result(request):
    return render(request, 'contact/contact_result.html')
