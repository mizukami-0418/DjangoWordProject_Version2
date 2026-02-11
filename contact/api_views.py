# contact/api_views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.core.mail import send_mail
from django.conf import settings
from .models import Inquiry
from .serializers import InquirySerializer, InquiryCreateSerializer
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class InquiryListAPIView(generics.ListAPIView):
    """
    ユーザー自身のお問い合わせ履歴を取得

    GET /api/contact/
    """

    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Inquiry.objects.filter(user=self.request.user).order_by("-created_at")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_inquiry(request):
    """
    お問い合わせを送信

    POST /api/contact/create/
    Body:
    {
        "subject": "件名",
        "context": "お問い合わせ内容"
    }
    """
    serializer = InquiryCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # お問い合わせを保存
    inquiry = Inquiry.objects.create(
        user=request.user,
        subject=data["subject"],
        context=data["context"],
    )

    # メール送信
    try:
        send_inquiry_emails(inquiry)
    except Exception as e:
        logger.error(f"Failed to send inquiry email: {str(e)}")
        # メール送信失敗してもお問い合わせは保存済みなのでエラーにしない

    return Response(InquirySerializer(inquiry).data, status=status.HTTP_201_CREATED)


def send_inquiry_emails(inquiry):
    """
    お問い合わせのメール通知を送信

    Args:
        inquiry: Inquiryオブジェクト
    """
    # 管理者向けメール
    admin_subject = f"【お問い合わせ】{inquiry.subject}"
    admin_message = f"""
新しいお問い合わせがありました。

━━━━━━━━━━━━━━━━━━━━━━
■ 件名
{inquiry.subject}

■ お問い合わせ内容
{inquiry.context}

■ ユーザー情報
メールアドレス: {inquiry.user.email}
ユーザー名: {inquiry.user.username}

■ お問い合わせ日時
{timezone.localtime(inquiry.created_at).strftime("%Y年%m月%d日 %H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━━━

管理画面で確認: {
        settings.ADMIN_URL if hasattr(settings, "ADMIN_URL") else "Django Admin"
    }
    """.strip()

    # ユーザー向け自動返信メール
    user_subject = f"お問い合わせを受け付けました - {inquiry.subject}"
    user_message = f"""
{inquiry.user.username} 様

お問い合わせいただきありがとうございます。
以下の内容でお問い合わせを受け付けました。

━━━━━━━━━━━━━━━━━━━━━━
■ 件名
{inquiry.subject}

■ お問い合わせ内容
{inquiry.context}

■ お問い合わせ日時
{timezone.localtime(inquiry.created_at).strftime("%Y年%m月%d日 %H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━━━

内容を確認の上、順次ご対応させていただきます。
今しばらくお待ちください。

※このメールは自動送信されています。
返信いただいても対応できませんのでご了承ください。

━━━━━━━━━━━━━━━━━━━━━━
ことばポケット運営事務局
━━━━━━━━━━━━━━━━━━━━━━
    """.strip()

    # メール送信
    try:
        # 管理者へ通知
        if hasattr(settings, "ADMIN_EMAIL") and settings.ADMIN_EMAIL:
            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            logger.info(f"Admin notification email sent for inquiry {inquiry.id}")

        # ユーザーへ自動返信
        send_mail(
            subject=user_subject,
            message=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.user.email],
            fail_silently=False,
        )
        logger.info(f"User confirmation email sent for inquiry {inquiry.id}")

    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        raise
