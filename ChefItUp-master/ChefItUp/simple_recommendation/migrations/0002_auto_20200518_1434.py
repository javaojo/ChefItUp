# Generated by Django 3.0.5 on 2020-05-18 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simple_recommendation', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='popularrecipe',
            index=models.Index(fields=['-fav_count'], name='simple_reco_fav_cou_0e1e9c_idx'),
        ),
    ]