from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("restaurantes", "0002_hu06_aprovacao")]

    operations = [
        migrations.RenameField(
            model_name="restaurante", old_name="categoria", new_name="tipo_cozinha",
        ),
        migrations.RenameField(
            model_name="restaurante", old_name="solicitante", new_name="criado_por",
        ),
        migrations.AlterField(
            model_name="restaurante", name="criado_por",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="restaurantes_criados", to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
