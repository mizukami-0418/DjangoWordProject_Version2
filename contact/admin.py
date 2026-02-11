# Register your models here.
# contact/admin.py

from django.contrib import admin
from .models import Inquiry


class InquiryAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "created_at")
    search_fields = ("user", "subject")
    list_filter = ("created_at",)


admin.site.register(Inquiry, InquiryAdmin)
