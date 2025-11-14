
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Client
from .forms import ClientForm
from django.contrib.auth import get_user_model

def staff_required(view_func):
	return login_required(user_passes_test(lambda u: u.is_staff)(view_func))

def home(request):
	return render(request, 'oauth2_service/home.html')

@staff_required
def client_detail(request, pk):
	client = get_object_or_404(Client, pk=pk)
	return render(request, 'oauth2_service/client_detail.html', {'client': client})

@staff_required
def client_list(request):
	clients = Client.objects.all().order_by('-created_at')
	return render(request, 'oauth2_service/client_list.html', {'clients': clients})

@staff_required
def client_create(request):
	if request.method == 'POST':
		form = ClientForm(request.POST)
		if form.is_valid():
			client = form.save()
			return redirect(reverse('client_list'))
	else:
		form = ClientForm()
	return render(request, 'oauth2_service/client_form.html', {'form': form, 'action': 'Tạo mới'})

@staff_required
def client_update(request, pk):
	client = get_object_or_404(Client, pk=pk)
	if request.method == 'POST':
		form = ClientForm(request.POST, instance=client)
		if form.is_valid():
			form.save()
			return redirect(reverse('client_list'))
	else:
		form = ClientForm(instance=client)
	return render(request, 'oauth2_service/client_form.html', {'form': form, 'action': 'Chỉnh sửa'})


@staff_required
def client_delete(request, pk):
	client = get_object_or_404(Client, pk=pk)
	if request.method == 'POST':
		client.delete()
		return redirect(reverse('client_list'))
	return render(request, 'oauth2_service/client_confirm_delete.html', {'client': client})

# --- OAuth2 Endpoints ---
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.utils.crypto import get_random_string
from urllib.parse import urlencode
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from .models import Client
import datetime

# Lưu tạm mã xác nhận và token (demo, nên dùng DB/session thực tế)
AUTHORIZATION_CODES = {}
ACCESS_TOKENS = {}

@require_http_methods(["GET", "POST"])
def oauth2_authorize(request):
	if request.method == "GET":
		client_id = request.GET.get("client_id")
		redirect_uri = request.GET.get("redirect_uri")
		scope = request.GET.get("scope")
		state = request.GET.get("state")
		client = Client.objects.filter(client_id=client_id, is_active=True).first()
		if not client:
			return HttpResponse("Invalid client_id", status=400)
		if not redirect_uri or redirect_uri not in client.redirect_uris.split():
			return HttpResponse("Invalid redirect_uri", status=400)
		if not request.user.is_authenticated:
			# Chuyển hướng đến trang login, sau đó quay lại authorize
			from urllib.parse import quote
			next_param = quote(request.get_full_path(), safe='')
			login_url = reverse('login') + f'?next={next_param}'
			return redirect(login_url)
		# Hiển thị xác nhận cấp quyền
		scope_list = scope.split() if scope else []
		return render(request, 'oauth2_service/authorize_confirm.html', {
			'client': client,
			'redirect_uri': redirect_uri,
			'scope': scope,
			'scope_list': scope_list,
			'state': state,
		})
	elif request.method == "POST":
		client_id = request.POST.get("client_id")
		redirect_uri = request.POST.get("redirect_uri")
		scope = request.POST.get("scope")
		state = request.POST.get("state")
		allow = request.POST.get("allow")
		client = Client.objects.filter(client_id=client_id, is_active=True).first()
		if not client or not redirect_uri or redirect_uri not in client.redirect_uris.split():
			return HttpResponse("Invalid request", status=400)
		if allow == "yes":
			code = get_random_string(32)
			AUTHORIZATION_CODES[code] = {
				"user_id": request.user.id,
				"client_id": client_id,
				"scope": scope,
				"expires": datetime.datetime.now() + datetime.timedelta(minutes=5)
			}
			params = {"code": code}
			if state:
				params["state"] = state
			return redirect(f"{redirect_uri}?{urlencode(params)}")
		else:
			return HttpResponse("Access denied", status=403)

@csrf_exempt
@require_http_methods(["POST"])
def oauth2_token(request):
	code = request.POST.get("code")
	client_id = request.POST.get("client_id")
	client_secret = request.POST.get("client_secret")
	client = Client.objects.filter(client_id=client_id, client_secret=client_secret, is_active=True).first()
	code_data = AUTHORIZATION_CODES.get(code)
	if not client or not code_data:
		return JsonResponse({"error": "invalid_grant"}, status=400)
	if code_data["client_id"] != client_id or code_data["expires"] < datetime.datetime.now():
		return JsonResponse({"error": "invalid_grant"}, status=400)
	# Tạo access token
	access_token = get_random_string(40)
	ACCESS_TOKENS[access_token] = {
		"user_id": code_data["user_id"],
		"client_id": client_id,
		"scope": code_data["scope"],
		"expires": datetime.datetime.now() + datetime.timedelta(hours=1)
	}
	# Xóa mã xác nhận đã dùng
	del AUTHORIZATION_CODES[code]
	return JsonResponse({
		"access_token": access_token,
		"token_type": "Bearer",
		"expires_in": 3600,
		"scope": code_data["scope"]
	})

@csrf_exempt
def userinfo(request):
	auth_header = request.META.get('HTTP_AUTHORIZATION', '')
	if auth_header.startswith('Bearer '):
		token = auth_header[7:]
		token_data = ACCESS_TOKENS.get(token)
		if token_data and token_data["expires"] > datetime.datetime.now():
			user = get_user_model().objects.filter(id=token_data["user_id"]).first()
			if user:
				return JsonResponse({
					"sub": user.id,
					"username": user.username,
					"email": user.email,
					"scope": token_data["scope"]
				})
	return JsonResponse({"error": "Unauthorized"}, status=401)
