# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.views.decorators.http import require_POST

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                # Mettre à jour le profil
                profile = user.profile
                profile.user_type = form.cleaned_data['user_type']
                profile.phone = form.cleaned_data.get('phone', '')
                profile.country = form.cleaned_data.get('country', '')
                profile.city = form.cleaned_data.get('city', '')
                profile.company_name = form.cleaned_data.get('company_name', '')
                profile.bio = form.cleaned_data.get('bio', '')
                profile.save()

                messages.success(request, "Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                return redirect('custom-login')

            except Exception as e:
                messages.error(request, f"Erreur lors de la création du compte : {str(e)}")

        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field} : {error}")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

# accounts/views.py

# accounts/views.py

@login_required
def profile(request):
    """Vue principale du profil avec gestion de la mise à jour"""
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profile')  # Rediriger vers la même page
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'active_tab': request.GET.get('tab', 'info')  # Pour garder l'onglet actif
    }
    return render(request, 'accounts/profile.html', context)

# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm

@login_required
def profile_update(request):
    """
    Vue dédiée à la modification du profil
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profile')  # Redirige vers la page de profil
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user': request.user
    }
    return render(request, 'accounts/profile_update.html', context)
# Vous pouvez garder cette vue si vous en avez besoin ailleurs
@login_required
@require_POST
def profile_update_api(request):
    """API pour mettre à jour le profil (AJAX) - Gardé pour compatibilité"""
    return JsonResponse({'status': 'error', 'message': 'Cette API est dépréciée'}, status=410)

def public_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    products = []
    requests = []
    
    try:
        if user.profile.user_type == 'fournisseur':
            from marketplace.models import Product
            products = Product.objects.filter(supplier=user, is_active=True)
        else:
            from marketplace.models import Request
            requests = Request.objects.filter(buyer=user, is_active=True)
    except:
        pass
    
    context = {
        'profile_user': user,
        'products': products,
        'requests': requests
    }
    return render(request, 'accounts/public_profile.html', context)

def custom_login(request):
    """Vue de connexion personnalisée avec authentification par email"""
    
    # Si l'utilisateur est déjà connecté
    if request.user.is_authenticated:
        try:
            if request.user.profile.user_type == 'fournisseur':
                return redirect('supplier-dashboard')
        except:
            pass
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('login')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        # Validation de base
        if not email or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'accounts/login.html')
        
        # Chercher l'utilisateur par email
        try:
            user = User.objects.get(email=email)
            
            # Authentifier avec le nom d'utilisateur
            authenticated_user = authenticate(
                request, 
                username=user.username, 
                password=password
            )
            
            if authenticated_user is not None:
                # Connexion réussie
                login(request, authenticated_user)
                
                # Gérer "Se souvenir de moi"
                if not remember:
                    request.session.set_expiry(0)  # Session expire à la fermeture
                else:
                    request.session.set_expiry(1209600)  # 2 semaines
                
                messages.success(
                    request, 
                    f'Bienvenue {authenticated_user.username} ! Connexion réussie.'
                )
                
                # Redirection selon le type d'utilisateur
                try:
                    if authenticated_user.profile.user_type == 'fournisseur':
                        return redirect('supplier-dashboard')
                except:
                    pass
                return redirect('home')
            else:
                messages.error(request, 'Mot de passe incorrect.')
                
        except User.DoesNotExist:
            messages.error(request, f'Aucun compte trouvé avec l\'email "{email}".')
        except Exception as e:
            messages.error(request, f'Erreur de connexion: {str(e)}')
    
    return render(request, 'accounts/login.html')

# accounts/views.py - Commentez ou supprimez ces lignes
"""
def google_login(request):
    # Redirection vers la connexion Google
    return redirect('/accounts/google/login/')  # ← Ceci crée la boucle
"""

def custom_logout(request):
    """Vue de déconnexion personnalisée"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')

@login_required
@require_POST
def change_password(request):
    """Vue pour changer le mot de passe"""
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        user = form.save()
        # Mettre à jour la session pour éviter la déconnexion
        update_session_auth_hash(request, user)
        return JsonResponse({'status': 'success', 'message': 'Mot de passe changé avec succès'})
    else:
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list[0]
        return JsonResponse({'status': 'error', 'errors': errors}, status=400)