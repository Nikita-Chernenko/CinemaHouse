# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-18 10:39
from __future__ import unicode_literals

import datetime
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0006_compensate_for_0003_bytestring_bug'),
        ('cinema_place', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='city',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='cities_light.City'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='area',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='cities_light.Country'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cinema',
            name='area',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='cinema_place.Area'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cinema',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(default='POINT(49.988358 36.232845)', srid=4326),
        ),
        migrations.AddField(
            model_name='cinema',
            name='name',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cinema_place.Brand'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='film',
            name='name',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filmcinema',
            name='cinema',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='cinema_place.Cinema'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filmcinema',
            name='date_release',
            field=models.DateField(default=datetime.datetime(2017, 6, 18, 0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filmcinema',
            name='name',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='cinema_place.Film'),
            preserve_default=False,
        ),
    ]