# Generated by Django 3.2.7 on 2021-10-17 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_controller', '0005_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
