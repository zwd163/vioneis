# Generated by Django 4.1.2 on 2025-04-06 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_listmodel_email_listmodel_password_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listmodel',
            name='check_code',
            field=models.IntegerField(blank=True, default=8888, null=True, verbose_name='Check Code'),
        ),
        migrations.AlterField(
            model_name='listmodel',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='listmodel',
            name='openid',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Openid'),
        ),
        migrations.AlterField(
            model_name='listmodel',
            name='password',
            field=models.CharField(default=1234, max_length=128, verbose_name='Password'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listmodel',
            name='staff_name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Staff Name/Username'),
        ),
        migrations.AlterField(
            model_name='typelistmodel',
            name='openid',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Openid'),
        ),
    ]
