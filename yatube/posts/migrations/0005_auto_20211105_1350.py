# Generated by Django 2.2.16 on 2021-11-05 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20211103_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, help_text='Дата и время присвоены автоматически', verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Введите текст', max_length=200, verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, help_text='Дата и время присвоены автоматически', verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Введите текст', max_length=400, verbose_name='Текст'),
        ),
    ]
