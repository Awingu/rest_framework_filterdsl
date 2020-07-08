# Generated by Django 2.1.7 on 2019-03-11 18:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rest_framework_filterdsl_tests', '0002_animalmodel_favorite_food'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='animalmodel',
            name='feeding_time',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='animalmodel',
            name='temperature',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='animalmodel',
            name='keeper',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='kept_animals', to='rest_framework_filterdsl_tests.Person'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='animalmodel',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='owned_animals', to='rest_framework_filterdsl_tests.Person'),
            preserve_default=False,
        ),
    ]