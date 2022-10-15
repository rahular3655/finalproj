# Generated by Django 4.0.7 on 2022-10-13 04:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extra', '0005_alter_offercategory_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offercategory',
            name='discount',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(30)]),
        ),
        migrations.AlterField(
            model_name='offerproduct',
            name='discount',
            field=models.IntegerField(default=0, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(30)]),
        ),
    ]
