# Generated by Django 3.0.4 on 2020-03-20 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terra_geocrud', '0036_auto_20191210_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='crudview',
            name='name_plural',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
