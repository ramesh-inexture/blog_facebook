# Generated by Django 4.0.5 on 2022-06-17 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_alter_uploadedfiles_post_alter_uploadedfiles_post_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfiles',
            name='post_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts_files', to='posts.posts'),
        ),
    ]
