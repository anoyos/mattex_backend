# Generated by Django 4.0.4 on 2022-07-18 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SMMapp', '0027_submission_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reviewer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewer_id', models.IntegerField(blank=True, null=True, verbose_name='Reviewer project id')),
                ('primary_name', models.CharField(max_length=255, verbose_name='Primary name')),
                ('secondary_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Secondary name')),
                ('short_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Short name')),
            ],
        ),
    ]
