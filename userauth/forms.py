from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class BootstrapMixin:
    """Tự thêm class form-control cho mọi trường."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class RegisterForm(UserCreationForm, BootstrapMixin):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(BootstrapMixin, AuthenticationForm):
    pass