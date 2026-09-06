from django import forms
from .models import Medicine, FoodItem
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a username'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Create password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm password'

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'quantity', 'expiry_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Paracetamol 500mg'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10', 'min': '1'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'name': 'Medicine Name',
            'quantity': 'Quantity',
            'expiry_date': 'Expiry Date',
        }

class FoodForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'quantity', 'expiry_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Milk, Bread, Rice'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2', 'min': '1'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'name': 'Food Name',
            'quantity': 'Quantity',
            'expiry_date': 'Expiry Date',
        }
