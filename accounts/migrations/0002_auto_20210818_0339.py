# Generated by Django 3.1.9 on 2021-08-18 03:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_waitlisted',
            field=models.BooleanField(default=True, help_text='Designates whether this user is in waitlist', verbose_name='Waitlist'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_posting_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('payment_status', models.IntegerField(choices=[(0, 'unpaid'), (1, 'requesting'), (2, 'paid')], default=0)),
                ('note', models.CharField(blank=True, max_length=500)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('user_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payouts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
