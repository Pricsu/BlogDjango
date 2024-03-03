# Generated by Django 5.0.1 on 2024-02-10 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='follows',
            field=models.ManyToManyField(blank=None, related_name='followed_by', to='users.profile'),
        ),
    ]
