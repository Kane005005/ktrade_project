from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    user_type = forms.ChoiceField(choices=Profile.UserType.choices, initial=Profile.UserType.VENDEUR)
    phone = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=200, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    # Vérifier doublon username
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Le nom d'utilisateur '{username}' est déjà pris.")
        return username

    # Vérifier doublon email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"L'email '{email}' est déjà utilisé.")
        return email


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user_type', 'phone', 'country', 'city', 'company_name', 'bio', 'profile_picture']
        widgets = {
            'user_type': forms.HiddenInput(),  # Champ caché
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pays'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom de l'entreprise"}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Bio'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionnel : vous pouvez aussi définir la valeur initiale
        if self.instance:
            self.fields['user_type'].initial = self.instance.user_type
        

# accounts/forms.py
from allauth.socialaccount.forms import SignupForm
from django import forms

class CustomSocialSignupForm(SignupForm):
    """
    Formulaire personnalisé pour demander le type d'utilisateur
    après l'inscription via Google
    """
    USER_TYPES = (
        ('vendeur', 'Vendeur - Je veux vendre des produits'),
        ('fournisseur', 'Fournisseur - Je veux proposer des produits en gros'),
    )
    
    user_type = forms.ChoiceField(
        choices=USER_TYPES,
        required=True,
        label="Vous êtes",
        widget=forms.RadioSelect,  # Boutons radio pour un choix clair
        initial='vendeur'
    )
    
    phone = forms.CharField(
        max_length=20, 
        required=False,
        label="Téléphone",
        widget=forms.TextInput(attrs={'placeholder': 'Optionnel'})
    )
    
    country = forms.CharField(
        max_length=100, 
        required=True,
        label="Pays",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: France'})
    )
    
    city = forms.CharField(
        max_length=100, 
        required=True,
        label="Ville",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Paris'})
    )
    
    company_name = forms.CharField(
        max_length=200, 
        required=False,
        label="Nom de l'entreprise",
        widget=forms.TextInput(attrs={'placeholder': 'Uniquement pour les fournisseurs'})
    )
    
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Parlez-nous de votre activité...'}),
        required=False,
        label="Bio / Description"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le champ email en lecture seule car il vient de Google
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].help_text = "Votre email Google (non modifiable)"
    
    def save(self, request):
        # Sauvegarder d'abord l'utilisateur
        user = super().save(request)
        
        # Mettre à jour le profil avec les données du formulaire
        profile = user.profile
        profile.user_type = self.cleaned_data['user_type']
        profile.phone = self.cleaned_data.get('phone', '')
        profile.country = self.cleaned_data.get('country', '')
        profile.city = self.cleaned_data.get('city', '')
        profile.company_name = self.cleaned_data.get('company_name', '')
        profile.bio = self.cleaned_data.get('bio', '')
        profile.save()
        
        # Ajouter un message de bienvenue personnalisé
        from django.contrib import messages
        messages.success(
            request, 
            f"Bienvenue {user.first_name or user.email} ! Votre compte {profile.get_user_type_display()} a été créé."
        )
        
        return user