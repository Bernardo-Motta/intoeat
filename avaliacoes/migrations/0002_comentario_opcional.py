from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("avaliacoes", "0001_initial")]
    operations = [
        migrations.AlterField(
            model_name="avaliacao", name="comentario", field=models.TextField(blank=True),
        ),
    ]
