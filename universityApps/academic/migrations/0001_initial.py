# Generated by Django 5.1.6 on 2025-04-19 23:57

import django.db.models.deletion
import universityApps.courses.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the academic year', max_length=50, verbose_name='Academic Year Name')),
                ('start_date', models.DateField(help_text='Start date of the academic year', verbose_name='Start Date')),
                ('end_date', models.DateField(help_text='End date of the academic year', verbose_name='End Date')),
                ('is_current', models.BooleanField(default=False, help_text='Whether the academic year is current', verbose_name='Is Current')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Time when the academic year was created', verbose_name='Created At')),
            ],
            options={
                'verbose_name': 'Academic Year',
                'verbose_name_plural': 'Academic Years',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='SemesterCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', universityApps.courses.fields.OrderField(blank=True)),
                ('is_required', models.BooleanField(default=True, help_text='Is the course required for the semester plan?', verbose_name='Required')),
                ('code', models.CharField(blank=True, editable=False, help_text='Code of the course', null=True, verbose_name='Code')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the semester course was created', verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When the semester course was last updated', verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Semester Course',
                'verbose_name_plural': 'Semester Courses',
                'ordering': ['semester_plan', 'order'],
            },
        ),
        migrations.CreateModel(
            name='SemesterPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, help_text='Name of the semester plan', max_length=255, verbose_name='Name')),
                ('semester_type', models.IntegerField(choices=[(1, 'First'), (2, 'Second'), (3, 'Summer')], help_text='Type of the semester', verbose_name='Semester Type')),
                ('order', models.PositiveSmallIntegerField(editable=False, help_text='Order of the semester plan', verbose_name='Order')),
                ('recommended_credits', models.PositiveIntegerField(default=15, help_text='Recommended number of credits for this semester', verbose_name='Recommended Credits')),
                ('min_credits', models.PositiveIntegerField(default=12, help_text='Minimum number of credits required for this semester', verbose_name='Minimum Credits')),
                ('max_credits', models.PositiveIntegerField(default=18, help_text='Maximum number of credits allowed for this semester', verbose_name='Maximum Credits')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Semester Plan',
                'verbose_name_plural': 'Semester Plans',
                'ordering': ['academic_level', 'semester_type'],
            },
        ),
        migrations.CreateModel(
            name='StudyPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, help_text='Name of the study plan', max_length=255, verbose_name='Name')),
                ('name_en', models.CharField(editable=False, help_text='Name of the study plan', max_length=255, null=True, verbose_name='Name')),
                ('name_ar', models.CharField(editable=False, help_text='Name of the study plan', max_length=255, null=True, verbose_name='Name')),
                ('version', models.PositiveSmallIntegerField(default=1, verbose_name='Version')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')], default='draft', max_length=20, verbose_name='Status')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('effective_from', models.DateField(verbose_name='Effective Date')),
            ],
            options={
                'verbose_name': 'Study Plan',
                'verbose_name_plural': 'Study Plans',
                'ordering': ['-effective_from', 'version'],
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester_type', models.CharField(choices=[(1, 'First'), (2, 'Second'), (3, 'Summer')], help_text='Type of the semester', max_length=50, verbose_name='Semester Type')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(verbose_name='End Date')),
                ('registration_start_date', models.DateField(verbose_name='Registration Start Date')),
                ('registration_end_date', models.DateField(verbose_name='Registration End Date')),
                ('final_exams_start_date', models.DateField(verbose_name='Final Exams Start Date')),
                ('final_exams_end_date', models.DateField(verbose_name='Final Exams End Date')),
                ('grades_due_date', models.DateField(verbose_name='Grades Due Date')),
                ('is_current', models.BooleanField(default=False, verbose_name='Is Current Semester')),
                ('academic_year', models.ForeignKey(help_text='Academic year to which the semester belongs', on_delete=django.db.models.deletion.CASCADE, to='academic.academicyear', verbose_name='Academic Year')),
            ],
            options={
                'verbose_name': 'Semester',
                'verbose_name_plural': 'Semesters',
                'ordering': ['academic_year', 'start_date'],
            },
        ),
    ]
