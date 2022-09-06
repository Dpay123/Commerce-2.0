# Generated by Django 4.0.4 on 2022-09-06 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_listing_category_alter_listing_current_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('Toys', 'Toys'), ('Misc', 'Misc'), ('Other', 'Other'), ('Home', 'Home'), ('Fashion', 'Fashion'), ('Electronics', 'Electronics')], default='Misc', max_length=64, null=True),
        ),
    ]
