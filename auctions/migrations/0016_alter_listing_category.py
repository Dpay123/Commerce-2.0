# Generated by Django 4.1 on 2022-09-13 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_alter_listing_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(default=(), on_delete=django.db.models.deletion.RESTRICT, to='auctions.category'),
        ),
    ]
