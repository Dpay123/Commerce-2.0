# Generated by Django 4.0.4 on 2022-05-03 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_comment_comment_on_alter_listing_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('Toys', 'Toys'), ('Home', 'Home'), ('Electronics', 'Electronics'), ('Fashion', 'Fashion')], max_length=64, null=True),
        ),
    ]