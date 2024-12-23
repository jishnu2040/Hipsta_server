# Generated by Django 5.1.2 on 2024-12-11 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_appointment_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='payment_method',
            field=models.CharField(choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('strip', 'Strip'), ('cash', 'Cash'), ('bank_transfer', 'Bank Transfer')], default='credit_card', max_length=50, verbose_name='Payment Method'),
        ),
    ]
