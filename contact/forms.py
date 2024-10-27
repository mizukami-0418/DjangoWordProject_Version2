# contact/forms.py

from django import forms
from .models import Inquiry

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['subject', 'context']
        labels = {
            'subject': '件名',
            'context': '問い合わせ内容',
        }
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': '件名', 'class': 'form-control'}),
            'context': forms.Textarea(attrs={'placeholder': 'お問い合わせ内容をご記入ください', 'class': 'form-control'}),
        }
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject) < 5:
            raise forms.ValidationError('件名は５文字以上で入力してください')
        return subject
    
    def clean_context(self):
        context = self.cleaned_data.get('context')
        if len(context) < 10:
            raise forms.ValidationError('問い合わせ内容は10文字以上で入力して下さい')
        return context
