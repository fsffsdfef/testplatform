# Generated by Django 4.1.7 on 2024-09-30 08:04

from django.db import migrations, models
import django.db.models.deletion
import utils.random_number


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portName', models.CharField(help_text='接口名', max_length=30, verbose_name='接口名')),
                ('portMethod', models.CharField(choices=[('POST', 'post'), ('GET', 'get'), ('UPDATE', 'update'), ('DELETE', 'delete')], default='POST', help_text='请求方式', max_length=30, verbose_name='请求方式')),
                ('portIntroduction', models.CharField(help_text='接口介绍', max_length=100, null=True, verbose_name='接口介绍')),
                ('apply', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='port', to='common.apply')),
            ],
            options={
                'db_table': 'test_port',
            },
        ),
        migrations.CreateModel(
            name='InterfaceHttpCases',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('create_user', models.CharField(max_length=20, verbose_name='创建人')),
                ('update_user', models.CharField(max_length=20, verbose_name='修改人')),
                ('caseId', models.CharField(help_text='接口用例id', max_length=6, primary_key=True, serialize=False, verbose_name='接口用例id')),
                ('caseName', models.CharField(help_text='用例名称', max_length=50, unique=True, verbose_name='用例名称')),
                ('headers', models.JSONField(help_text='头部信息', null=True, verbose_name='请求头')),
                ('body', models.JSONField(help_text='请求体', null=True, verbose_name='请求体')),
                ('timeOut', models.IntegerField(default=5, help_text='超时时间', verbose_name='超时时间')),
                ('retries', models.IntegerField(default=0, help_text='重试次数', verbose_name='重试次数')),
                ('port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='httpCase', to='automation.port')),
            ],
            options={
                'db_table': 'interface_http_cases',
            },
            bases=(models.Model, utils.random_number.RandomNumber),
        ),
        migrations.CreateModel(
            name='ExpressItem',
            fields=[
                ('expressItemId', models.CharField(max_length=8, primary_key=True, serialize=False, verbose_name='规则组id')),
                ('httpCase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expressItem', to='automation.interfacehttpcases')),
            ],
            options={
                'db_table': 'test_expressitem',
            },
            bases=(models.Model, utils.random_number.RandomNumber),
        ),
        migrations.CreateModel(
            name='Expresses',
            fields=[
                ('expressId', models.CharField(max_length=7, primary_key=True, serialize=False, verbose_name='表达式')),
                ('matchKey', models.CharField(help_text='需要校验的key', max_length=20, verbose_name='匹配建')),
                ('matchValue', models.CharField(help_text='预期返回的值', max_length=20, verbose_name='匹配值')),
                ('keyType', models.CharField(help_text='需断言字段的类型', max_length=20, verbose_name='字段类型')),
                ('matchOper', models.CharField(help_text='运算校验的方法', max_length=10, verbose_name='计算方法')),
                ('expressItem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expressList', to='automation.expressitem')),
            ],
            options={
                'db_table': 'test_expresses',
            },
            bases=(models.Model, utils.random_number.RandomNumber),
        ),
    ]
