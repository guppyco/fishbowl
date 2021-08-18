# Generated by Django 3.1.9 on 2021-08-18 11:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20210818_0339'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayoutRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('payment_status', models.IntegerField(choices=[(0, 'requesting'), (1, 'paid')], default=0)),
                ('note', models.CharField(blank=True, max_length=500)),
                ('user_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payout_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
