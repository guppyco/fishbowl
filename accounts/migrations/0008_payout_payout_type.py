# Generated by Django 3.1.14 on 2022-07-04 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20211116_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='payout',
            name='payout_type',
            field=models.CharField(blank=True, default='activities', max_length=100),
        ),
    ]