# Generated by Django 4.0.4 on 2022-05-02 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('Toys', 'Toys'), ('Fashion', 'Fashion'), ('Electronics', 'Electronics'), ('Home', 'Home')], max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='img_url',
            field=models.URLField(blank=True),
        ),
    ]