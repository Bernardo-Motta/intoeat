from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("avaliacoes", "0002_comentario_opcional")]
    operations = [
        migrations.AddIndex(
            model_name="avaliacao",
            index=models.Index(fields=["restaurante", "usuario", "-data", "-id"], name="avaliacao_vigente_idx"),
        ),
    ]
