# contact/api_urls.py

from django.urls import path
from .api_views import InquiryListAPIView, create_inquiry

app_name = "contact_api"

urlpatterns = [
    # お問い合わせ履歴
    path("", InquiryListAPIView.as_view(), name="inquiry_list"),
    # お問い合わせ送信
    path("create/", create_inquiry, name="create_inquiry"),
]
