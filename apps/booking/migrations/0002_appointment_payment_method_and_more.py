# Generated by Django 5.1.2 on 2024-12-05 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='payment_method',
            field=models.CharField(choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('paypal', 'PayPal'), ('cash', 'Cash'), ('bank_transfer', 'Bank Transfer')], default='credit_card', max_length=50, verbose_name='Payment Method'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20, verbose_name='Payment Status'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='payment_transaction_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Payment Transaction ID'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Total Amount'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='end_time',
            field=models.TimeField(verbose_name='End Time'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='start_time',
            field=models.TimeField(verbose_name='Start Time'),
        ),
    ]