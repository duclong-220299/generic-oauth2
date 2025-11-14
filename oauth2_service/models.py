
from django.db import models
import secrets

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
