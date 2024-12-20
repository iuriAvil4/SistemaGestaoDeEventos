# Generated by Django 5.1.4 on 2024-12-19 19:48

import datetime
import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(blank=True, default='', max_length=254, unique=True)),
                ('name', models.CharField(blank=True, default='', max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=15, unique=True)),
                ('profile_type', models.CharField(choices=[('ADMIN', 'Administrator'), ('ORGANIZER', 'Organizer'), ('PARTICIPANT', 'Participant')], default='PARTICIPANT', max_length=20)),
                ('date_joined', models.DateTimeField(default=datetime.datetime(2024, 12, 19, 19, 48, 25, 137363, tzinfo=datetime.timezone.utc))),
                ('is_active', models.BooleanField(default=True)),
                ('cnpj_cpf', models.CharField(blank=True, max_length=18, null=True)),
                ('business_name', models.CharField(blank=True, max_length=255, null=True)),
                ('commercial_address', models.TextField(blank=True, null=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='custom_user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='custom_user_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
    ]
