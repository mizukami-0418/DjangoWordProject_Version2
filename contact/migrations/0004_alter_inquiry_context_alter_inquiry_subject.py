# Generated by Django 5.1 on 2024-10-21 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0003_alter_inquiry_context_alter_inquiry_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inquiry',
            name='context',
            field=models.TextField(max_length=500, verbose_name='問い合わせ'),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='subject',
            field=models.CharField(max_length=50, verbose_name='件名'),
        ),
    ]