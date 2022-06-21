# Generated by Django 4.0.5 on 2022-06-21 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_alter_uploadedfiles_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostCategories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='posts',
            name='category_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.postcategories'),
        ),
    ]