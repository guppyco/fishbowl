# Generated by Django 3.1.9 on 2021-08-28 13:42

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=140)),
                ('answer', ckeditor.fields.RichTextField()),
                ('order', models.PositiveSmallIntegerField(default=0, unique=True)),
            ],
            options={
                'ordering': ['order', 'pk'],
            },
        ),
    ]
