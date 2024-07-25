# Generated by Django 4.1.7 on 2024-07-24 08:03

from django.db import migrations, models
import utils.random_number


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Depart',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('create_user', models.CharField(max_length=20, verbose_name='创建人')),
                ('update_user', models.CharField(max_length=20, verbose_name='修改人')),
                ('depart_id', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='部门ID')),
                ('depart_name', models.CharField(max_length=30, verbose_name='部门名')),
            ],
            options={
                'db_table': 't_depart',
            },
            bases=(models.Model, utils.random_number.RandomNumber),
        ),
    ]
