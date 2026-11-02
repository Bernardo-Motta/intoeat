from django.conf import settings
from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("restaurantes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(model_name="restaurante", name="cidade", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="restaurante", name="cnpj", field=models.CharField(blank=True, db_index=True, max_length=14)),
        migrations.AddField(model_name="restaurante", name="motivo_rejeicao", field=models.TextField(blank=True)),
        migrations.AddField(model_name="restaurante", name="solicitante", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="restaurantes_solicitados", to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="restaurante", name="status", field=models.CharField(choices=[("pendente", "Pendente"), ("aprovado", "Aprovado"), ("rejeitado", "Rejeitado")], db_index=True, default="pendente", max_length=10)),
        migrations.AlterField(model_name="restaurante", name="nome", field=models.CharField(db_index=True, max_length=120)),
        migrations.AddConstraint(model_name="restaurante", constraint=models.UniqueConstraint(condition=Q(status__in=["pendente", "aprovado"]) & ~Q(cnpj=""), fields=("cnpj",), name="cnpj_ativo_unico")),
    ]
