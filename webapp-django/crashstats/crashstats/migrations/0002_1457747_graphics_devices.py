# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-25 15:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crashstats', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraphicsDevice',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('vendor_hex', models.CharField(max_length=100)),
                ('adapter_hex', models.CharField(null=True, blank=True, max_length=100)),
                ('vendor_name', models.TextField(null=True, blank=True)),
                ('adapter_name', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='graphicsdevice',
            unique_together=set([('vendor_hex', 'adapter_hex')]),
        ),
    ]
