# Generated by Django 5.1.4 on 2024-12-31 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('script_generator', '0003_remove_blogpost_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='title',
        ),
        migrations.AddField(
            model_name='blogpost',
            name='external_link_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='file_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]