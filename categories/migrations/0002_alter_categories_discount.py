# Generated by Django 4.0.7 on 2022-09-27 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categories',
            name='discount',
            field=models.IntegerField(default=0, null=True),
        ),
    ]