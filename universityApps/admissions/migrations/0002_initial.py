# Generated by Django 5.1.6 on 2025-04-19 23:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admissions', '0001_initial'),
        ('programs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='admissionapplication',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admission_applications', to='programs.academicprogram', verbose_name='Program'),
        ),
    ]
