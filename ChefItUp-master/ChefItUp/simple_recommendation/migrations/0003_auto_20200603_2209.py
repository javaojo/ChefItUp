# Generated by Django 3.0.5 on 2020-06-03 22:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simple_recommendation', '0002_auto_20200518_1434'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='popularrecipe',
            options={'ordering': ['-fav_count']},
        ),
    ]