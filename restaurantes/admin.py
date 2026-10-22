from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import Ocasiao, Caracteristica, FotoRestaurante, Restaurante
from .services import aprovar_restaurante, rejeitar_restaurante

admin.site.register(Ocasiao)
admin.site.register(Caracteristica)

class FotoRestauranteInline(admin.TabularInline):
    model = FotoRestaurante
    extra = 1


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    inlines = [FotoRestauranteInline]
    list_display = ("nome", "cnpj", "status", "criado_por")
    list_filter = ("status",)
    search_fields = ("nome", "cnpj")
    readonly_fields = ("status", "motivo_rejeicao")
    actions = ["aprovar", "rejeitar"]

    @admin.action(description="Aprovar restaurantes selecionados")
    def aprovar(self, request, queryset):
        for restaurante in queryset:
            try:
                aprovar_restaurante(restaurante)
            except ValidationError as erro:
                self.message_user(request, f"{restaurante}: {erro}", level=messages.ERROR)

    @admin.action(description="Rejeitar restaurantes selecionados (motivo padrão)")
    def rejeitar(self, request, queryset):
        for restaurante in queryset:
            rejeitar_restaurante(restaurante, "Solicitação rejeitada pela equipe. Contate o suporte para detalhes.")
