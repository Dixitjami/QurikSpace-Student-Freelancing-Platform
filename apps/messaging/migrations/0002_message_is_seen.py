from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
    ]
