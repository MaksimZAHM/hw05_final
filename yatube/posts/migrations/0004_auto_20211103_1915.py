# Generated by Django 2.2.16 on 2021-11-03 16:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0003_auto_20211101_1755'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Группа'},
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Введите текст коммента', max_length=200, verbose_name='Текст коммента')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Дата и время присвоены автоматически', verbose_name='Дата и время публикации коммента')),
                ('author', models.ForeignKey(help_text='Этот пользователь оставил коммент', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор коммента')),
                ('post', models.ForeignKey(help_text='Этот пост комментим', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Пост')),
            ],
            options={
                'verbose_name': 'Коммент',
                'verbose_name_plural': 'Комменты',
                'ordering': ('-created',),
            },
        ),
    ]
