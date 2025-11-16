from django.contrib import admin
from .models import Client, AuthorizationCode, AccessToken

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
	list_display = ("name", "client_id", "is_active", "created_at")
	search_fields = ("name", "client_id")
	list_filter = ("is_active", "created_at")
	readonly_fields = ("client_id", "client_secret", "created_at")


@admin.register(AuthorizationCode)
class AuthorizationCodeAdmin(admin.ModelAdmin):
	list_display = ("code", "user", "client_id", "expires")
	search_fields = ("code", "user__username", "client_id")
	list_filter = ("expires",)
	readonly_fields = ("code", "user", "client_id", "scope", "expires")

@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
	list_display = ("token", "user", "client_id", "expires")
	search_fields = ("token", "user__username", "client_id")
	list_filter = ("expires",)
	readonly_fields = ("token", "user", "client_id", "scope", "expires")
	