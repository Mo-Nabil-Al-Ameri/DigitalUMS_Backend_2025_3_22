# Generated by Django 5.1.6 on 2025-04-19 23:57

import django.core.validators
import django.db.models.deletion
import universityApps.courses.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the item', max_length=250, verbose_name='Title')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(upload_to='files')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the item', max_length=250, verbose_name='Title')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(upload_to='images')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the module', max_length=255, verbose_name='Module Title')),
                ('description', models.TextField(blank=True, help_text='Description of the module', null=True, verbose_name='Module Description')),
                ('order', universityApps.courses.fields.OrderField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the module was created', verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When the module was last updated', verbose_name='Updated At')),
                ('photo', models.ImageField(blank=True, upload_to='Courses/Modules/photos/%Y/%m/%d/')),
            ],
            options={
                'verbose_name': 'Module',
                'verbose_name_plural': 'Modules',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the subject', max_length=200, verbose_name='Subject Name')),
                ('slug', models.SlugField(editable=False, help_text='Slug of the subject', max_length=250, unique=True, verbose_name='Subject Slug')),
                ('code', models.CharField(editable=False, help_text='Code of the subject', max_length=50, verbose_name='Subject Code')),
                ('type', models.CharField(choices=[('university', 'university Requirements'), ('college', 'college Requirements'), ('department', 'department Requirements'), ('specialization', 'specialization Requirements')], default='university', help_text='Type of the subject', max_length=20, verbose_name='Subject Type')),
            ],
            options={
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
                'ordering': ['name', 'code'],
            },
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the item', max_length=250, verbose_name='Title')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the item', max_length=250, verbose_name='Title')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('url', models.URLField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('order', universityApps.courses.fields.OrderField(blank=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='Content Type')),
            ],
            options={
                'verbose_name': 'Content',
                'verbose_name_plural': 'Contents',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the course', max_length=200, verbose_name='Course Name')),
                ('slug', models.SlugField(editable=False, help_text='Slug of the course', max_length=250, unique=True, verbose_name='Course Slug')),
                ('credits', models.PositiveSmallIntegerField(default=3, help_text='Number of credits for the course', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)], verbose_name='Credits')),
                ('hours_lecture', models.PositiveSmallIntegerField(default=3, help_text='Number of lecture hours for the course', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Lecture Hours')),
                ('hours_lab', models.PositiveSmallIntegerField(default=0, help_text='Number of lab hours for the course', verbose_name='Lab Hours')),
                ('practice_hours', models.PositiveSmallIntegerField(default=0, help_text='Number of practice hours for the course', verbose_name='Practice Hours')),
                ('code', models.CharField(blank=True, editable=False, help_text='Code of the course', null=True, unique=True, verbose_name='Course Code')),
                ('course_type', models.CharField(choices=[('mandatory', 'mandatory'), ('elective', 'elective'), ('optional', 'optional')], default='mandatory', help_text='Type of the course', max_length=20, verbose_name='Course Type')),
                ('overview', models.TextField(blank=True, help_text='Overview of the course', null=True, verbose_name='Overview')),
                ('is_active', models.BooleanField(default=True, help_text='Whether the course is active or not', verbose_name='Active')),
                ('syllabus_file', models.FileField(blank=True, null=True, upload_to='syllabi/', verbose_name='Syllabus File')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the course was created', verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When the course was last updated', verbose_name='Updated At')),
                ('learning_outcomes', models.TextField(blank=True, help_text='Learning outcomes for the course', verbose_name='Learning Outcomes')),
                ('corequisites', models.ManyToManyField(blank=True, help_text='Corequisites for the course', related_name='corequisite_for', to='courses.course', verbose_name='Corequisites')),
                ('prerequisites', models.ManyToManyField(blank=True, help_text='Prerequisites for the course', related_name='prerequisite_for', to='courses.course', verbose_name='Prerequisites')),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
                'ordering': ['-created_at', 'code'],
            },
        ),
    ]
