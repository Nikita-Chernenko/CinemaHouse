# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-18 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_place', '0004_auto_20170918_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filmpictures',
            name='picture',
            field=models.ImageField(upload_to='cinema_pictures'),
        ),
    ]