# Generated by Django 5.1.4 on 2024-12-30 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('script_generator', '0002_rename_youtube_link_blogpost_external_link_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='blogpost',
            name='external_title',
        ),
        migrations.AddField(
            model_name='blogpost',
            name='title',
            field=models.CharField(default='Default Title', max_length=255),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='external_link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
