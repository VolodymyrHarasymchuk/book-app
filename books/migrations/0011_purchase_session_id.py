# Generated by Django 5.0.4 on 2024-06-09 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_book_price_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='session_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
