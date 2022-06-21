# Generated by Django 4.0.5 on 2022-06-17 09:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_uploadedfiles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfiles',
            name='post',
            field=models.FileField(upload_to='posts'),
        ),
        migrations.AlterField(
            model_name='uploadedfiles',
            name='post_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hello', to='posts.posts'),
        ),
    ]
