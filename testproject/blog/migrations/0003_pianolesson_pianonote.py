# Generated by Django 5.0.3 on 2024-06-10 14:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_audio'),
    ]

    operations = [
        migrations.CreateModel(
            name='PianoLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='image/')),
                ('uploaded_at2', models.DateTimeField(auto_now_add=True)),
                ('sheet_music', models.FileField(upload_to='sheet_music/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PianoNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(max_length=10)),
                ('start_time', models.FloatField()),
                ('end_time', models.FloatField()),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='blog.pianolesson')),
            ],
        ),
    ]
