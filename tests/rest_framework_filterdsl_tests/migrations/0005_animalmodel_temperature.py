# Generated by Django 2.1.7 on 2019-03-11 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_framework_filterdsl_tests', '0004_auto_20190311_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalmodel',
            name='temperature',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
            preserve_default=False,
        ),
    ]
