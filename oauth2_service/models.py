import secrets
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Client(models.Model):
	name = models.CharField(max_length=100)
	client_id = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
	client_secret = models.CharField(max_length=128, default=secrets.token_urlsafe)
	redirect_uris = models.TextField(help_text="Danh sách URI, phân cách bằng dấu xuống dòng")
	scopes = models.CharField(max_length=256, help_text="Phạm vi truy cập, phân cách bằng dấu cách")
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.name} ({self.client_id})"

class AuthorizationCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    scope = models.TextField(blank=True, null=True)
    expires = models.DateTimeField()

    def is_expired(self):
        return self.expires < timezone.now()

class AccessToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    scope = models.TextField(blank=True, null=True)
    expires = models.DateTimeField()

    def is_expired(self):
        return self.expires < timezone.now()
