# Generated by Django 5.1 on 2024-09-14 08:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dictionary', '0002_level_description'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(max_length=10)),
                ('score', models.IntegerField(default=0)),
                ('total_questions', models.IntegerField(default=0)),
                ('current_question_index', models.IntegerField(default=0)),
                ('question_ids', models.TextField(blank=0, null=True)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.level')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ユーザー進行状況',
                'verbose_name_plural': 'ユーザー進行状況',
                'db_table': 'user_progress',
            },
        ),
    ]
