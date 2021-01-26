from django import forms
from django.core.validators import *
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'First Name', 'class': 'form-control input-shadow', 'autocomplete':'off'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class': 'form-control input-shadow', 'autocomplete':'off'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username', 'class': 'form-control input-shadow', 'autocomplete':'off'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email', 'class': 'form-control input-shadow', 'autocomplete':'off'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class': 'form-control input-shadow', 'autocomplete':'off'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm Password', 'class': 'form-control input-shadow', 'autocomplete': 'off'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter Username', 'class': 'form-control input-shadow', 'autocomplete':'off'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password','class': 'form-control input-shadow'}))

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('This user does not exist.')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect login credentials. Please try again!')
            if not user.is_active:
                raise forms.ValidationError('This user is not active.')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'groups',
            'is_staff',
            'is_superuser',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if email != email2:
            raise forms.ValidationError('E-Mails must match.')

        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError('E-Mail already exists.')
        return email

class AddPartForm(forms.ModelForm):
    partId = Part.objects.all().order_by("-partId")[0].partId+1
    partNo = forms.CharField(label='Part Number', max_length=20, widget=forms.TextInput(
        attrs={
            'class': 'form-control m-2'
        }
    ))
    supplierId = forms.ModelChoiceField(label='Part Supplier', queryset=Supplier.objects.all(), widget=forms.Select(
        attrs={
            'class': 'form-control m-2'
        }
    ))

    partDesc = forms.CharField(label='Part Name', max_length=50, widget=forms.TextInput(
        attrs={
            'class': 'form-control m-2'
        }
    ))
    partCost = forms.DecimalField(label='Cost/Part', max_digits=10, decimal_places=2, widget=forms.TextInput(
        attrs={
            'class': 'form-control m-2'
        }
    ))

    class Meta:
        model = Part
        fields = ['supplierId', 'partNo', 'partDesc', 'partCost']

class EditPartForm(forms.ModelForm):
    partNo = forms.CharField(label='Part Number', max_length=20, widget=forms.TextInput(
        attrs={
            'class': 'form-control m-2'
        }
    ))
    supplierId = forms.ModelChoiceField(label='Part Supplier', queryset=Supplier.objects.all(), widget=forms.Select(
        attrs={
            'class': 'form-control m-2'
        }
    ))

    partDesc = forms.CharField(label='Part Name', max_length=50, widget=forms.TextInput(
        attrs={
            'class': 'form-control m-2'
        }
    ))
    partCost = forms.DecimalField(label='Cost/Part', max_digits=10, decimal_places=2, widget=forms.TextInput(
        attrs={
            'class': 'form-control m-2'
        }
    ))

    quantity = forms.IntegerField(label='On Hand', widget=forms.TextInput(
        attrs={
            'class': 'form-control m-2'
        }
    ))

    class Meta:
        model = Part
        fields = ['supplierId', 'partNo', 'partDesc', 'partCost', 'quantity']

    def clean_quantity(self):
        return self.data['quantity']


class ReconcileForm(forms.ModelForm):

    class Meta:
        model = Reconcile
        fields = ['reconcileId', 'reconcileDate', 'reconciledBy']


def year_choices():
    return[(r,r) for r in range(2000, datetime.datetime.today().year+1)]


def current_year():
    return datetime.today().year

def current_month():
    return datetime.today().month

def previous_month():
    return datetime.today().month - 1

def current_week():
    return datetime.today().isocalendar()[1]

def max_value_current_yer(value):
    return MaxValueValidator(current_year())(value)

class RollingPartsSummary(forms.Form):
    location = forms.ModelChoiceField(label='Location', queryset=Locations.objects.all(), widget=forms.Select(
        attrs={
            'class': 'form-control m-2'
        }
    ))
    year = forms.TypedChoiceField(coerce=int, choices=year_choices, initial=current_year, label='Year', widget=forms.TextInput(
        attrs={
            'class': 'form-control m-2'
        }
    ))



