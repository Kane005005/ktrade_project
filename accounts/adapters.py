# accounts/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.contrib import messages
from django.contrib.auth.models import User  # Ajouté
from allauth.exceptions import ImmediateHttpResponse
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
                # Si le profil n'existe pas, rediriger vers la page d'accueil
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
        """
        Permettre l'inscription via réseaux sociaux
        """
        return True
    
    def pre_social_login(self, request, sociallogin):
        """
        Cette méthode est appelée avant la connexion/inscription sociale.
        On peut l'utiliser pour gérer les cas particuliers.
        """
        # Vérifier si l'utilisateur existe déjà avec cet email
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                # Si un utilisateur avec cet email existe déjà
                user = User.objects.get(email=email)
                
                # Si le compte social n'est pas déjà lié, on le lie
                if not sociallogin.is_existing:
                    sociallogin.connect(request, user)
                    messages.info(
                        request, 
                        f'Votre compte Google a été lié à votre compte existant.'
                    )
                    
                    # Vérifier si le profil a un type d'utilisateur
                    try:
                        if user.profile.user_type:
                            # Redirection directe
                            from django.http import HttpResponseRedirect
                            if user.profile.user_type == 'fournisseur':
                                raise ImmediateHttpResponse(HttpResponseRedirect('/supplier/dashboard/'))
                            else:
                                raise ImmediateHttpResponse(HttpResponseRedirect('/'))
                    except:
                        pass
                        
            except User.DoesNotExist:
                # Nouvel utilisateur, on continue l'inscription
                pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Sauvegarder l'utilisateur APRÈS le formulaire de finalisation
        """
        # Sauvegarder d'abord l'utilisateur de base
        user = super().save_user(request, sociallogin, form)
        
        # Maintenant le profil est créé (par le signal post_save)
        
        # Si nous avons un formulaire, c'est que nous venons de la page de signup
        if form:
            # Les données du profil sont déjà sauvegardées dans le formulaire
            # via CustomSocialSignupForm.save()
            pass
        else:
            # Si pas de formulaire (connexion directe avec compte existant)
            # Mettre à jour avec les infos Google
            if sociallogin.account.provider == 'google':
                data = sociallogin.account.extra_data
                
                # Mettre à jour les champs utilisateur
                if not user.first_name and data.get('given_name'):
                    user.first_name = data.get('given_name', '')
                if not user.last_name and data.get('family_name'):
                    user.last_name = data.get('family_name', '')
                user.save()
                
                # Mettre à jour le profil avec un type par défaut (si pas déjà défini)
                try:
                    profile = user.profile
                    if not profile.user_type:
                        # Type par défaut (vendeur)
                        profile.user_type = 'vendeur'
                        profile.save()
                except:
                    pass
        
        return user
    
    def get_signup_form_initial_data(self, request, sociallogin):
        """
        Remplir les données initiales du formulaire d'inscription
        avec les infos du compte Google
        """
        initial = super().get_signup_form_initial_data(request, sociallogin)
        
        if sociallogin.account.provider == 'google':
            data = sociallogin.account.extra_data
            
            # Pré-remplir avec les données Google
            initial['email'] = data.get('email', '')
            initial['username'] = data.get('email', '').split('@')[0]
            
            # Vous pouvez ajouter d'autres champs ici si nécessaire
        
        return initial
    
    def populate_user(self, request, sociallogin, data):
        """
        Peupler l'utilisateur avec les données sociales avant le formulaire
        """
        user = super().populate_user(request, sociallogin, data)
        
        if sociallogin.account.provider == 'google':
            data = sociallogin.account.extra_data
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('family_name', '')
        
        return user