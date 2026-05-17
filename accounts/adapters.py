# accounts/adapters.py

# ❌ ANCIEN IMPORT (à supprimer)
# from allauth.exceptions import ImmediateHttpResponse

# ✅ NOUVEL IMPORT (à utiliser)
from allauth.core.exceptions import ImmediateHttpResponse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """Redirige vers le tableau de bord approprié après connexion"""
        if request.user.is_authenticated:
            try:
                if hasattr(request.user, 'profile') and request.user.profile.user_type == 'fournisseur':
                    return resolve_url('supplier-dashboard')
                else:
                    return resolve_url('home')
            except (AttributeError, Exception):
                return resolve_url('home')
        return super().get_login_redirect_url(request)
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """Personnaliser les messages"""
        if message_template == 'account/messages/logged_in.txt':
            if request.user.is_authenticated:
                messages.success(request, f'Bienvenue {request.user.username} ! Connexion réussie.')
        else:
            super().add_message(request, level, message_template, message_context, extra_tags)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter personnalisé pour les inscriptions via réseaux sociaux
    """
    
    def is_open_for_signup(self, request, sociallogin):
        """Permettre l'inscription via réseaux sociaux"""
        return True
    
    def pre_social_login(self, request, sociallogin):
        """Gestion avant la connexion/inscription sociale"""
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                
                if not sociallogin.is_existing:
                    sociallogin.connect(request, user)
                    messages.info(
                        request, 
                        f'Votre compte Google a été lié à votre compte existant.'
                    )
                    
                    try:
                        if user.profile.user_type:
                            from django.http import HttpResponseRedirect
                            if user.profile.user_type == 'fournisseur':
                                raise ImmediateHttpResponse(HttpResponseRedirect('/marketplace/dashboard/'))
                            else:
                                raise ImmediateHttpResponse(HttpResponseRedirect('/'))
                    except:
                        pass
                        
            except User.DoesNotExist:
                pass
    
    def save_user(self, request, sociallogin, form=None):
        """Sauvegarder l'utilisateur après le formulaire de finalisation"""
        user = super().save_user(request, sociallogin, form)
        
        if form:
            pass
        else:
            if sociallogin.account.provider == 'google':
                data = sociallogin.account.extra_data
                
                if not user.first_name and data.get('given_name'):
                    user.first_name = data.get('given_name', '')
                if not user.last_name and data.get('family_name'):
                    user.last_name = data.get('family_name', '')
                user.save()
                
                try:
                    profile = user.profile
                    if not profile.user_type:
                        profile.user_type = 'vendeur'
                        profile.save()
                except:
                    pass
        
        return user
    
    def get_signup_form_initial_data(self, request, sociallogin):
        """Remplir les données initiales du formulaire"""
        initial = super().get_signup_form_initial_data(request, sociallogin)
        
        if sociallogin.account.provider == 'google':
            data = sociallogin.account.extra_data
            initial['email'] = data.get('email', '')
            initial['username'] = data.get('email', '').split('@')[0]
        
        return initial
    
    def populate_user(self, request, sociallogin, data):
        """Peupler l'utilisateur avec les données sociales"""
        user = super().populate_user(request, sociallogin, data)
        
        if sociallogin.account.provider == 'google':
            data = sociallogin.account.extra_data
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('family_name', '')
        
        return user