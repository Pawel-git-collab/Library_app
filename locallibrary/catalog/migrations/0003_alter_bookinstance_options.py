# Generated by Django 3.2.13 on 2022-04-30 00:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_book_language'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back'], 'permissions': (('can_mark_returned', 'Set book as returned'),)},
        ),
    ]