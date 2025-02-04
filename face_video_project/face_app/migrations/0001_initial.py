# Generated by Django 5.1.5 on 2025-01-26 08:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ComplaintTb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complaint_no', models.CharField(max_length=20, unique=True)),
                ('mobile', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=100)),
                ('umobile', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.TextField()),
                ('filename', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('status', models.CharField(choices=[('New Complaint', 'New Complaint'), ('Investigation in Progress', 'Investigation in Progress'), ('Face Matched', 'Face Matched'), ('Match Failed', 'Match Failed'), ('Closed', 'Closed')], default='New Complaint', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='RegTb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mobile', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.TextField()),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='InvestigationTb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_file', models.FileField(blank=True, null=True, upload_to='investigations/')),
                ('status', models.CharField(choices=[('Video Loaded', 'Video Loaded'), ('Face Matched', 'Face Matched'), ('Match Failed', 'Match Failed'), ('Closed', 'Closed')], default='Video Loaded', max_length=30)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investigation', to='face_app.complainttb')),
            ],
        ),
        migrations.AddField(
            model_name='complainttb',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='face_app.regtb'),
        ),
    ]
