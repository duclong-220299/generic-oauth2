from django import forms
from .models import Client

SCOPE_CHOICES = [
    ('read', 'Đọc dữ liệu'),
    ('write', 'Ghi dữ liệu'),
    ('delete', 'Xóa dữ liệu'),
    ('profile', 'Thông tin người dùng'),
    ('email', 'Email người dùng'),
]

class ClientForm(forms.ModelForm):
    scopes = forms.MultipleChoiceField(
        choices=SCOPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Phạm vi truy cập (scopes)'
    )

    class Meta:
        model = Client
        fields = [
            'name',
            'redirect_uris',
            'scopes',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên ứng dụng'}),
            'redirect_uris': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Mỗi dòng là một URI'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_scopes(self):
        scopes = self.cleaned_data['scopes']
        return ' '.join(scopes)

    def initial_scopes(self):
        if self.instance and self.instance.scopes:
            return self.instance.scopes.split()
        return []
