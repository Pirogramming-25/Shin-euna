from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ideas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devtool',
            name='kind',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='devtool',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='idea',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
