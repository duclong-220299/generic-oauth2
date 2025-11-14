from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
	list_display = ("name", "client_id", "is_active", "created_at")
	search_fields = ("name", "client_id")
	list_filter = ("is_active", "created_at")
	readonly_fields = ("client_id", "client_secret", "created_at")
