# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
import logging

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile

# Configuration du logger
logger = logging.getLogger(__name__)


# accounts/views.py - fonction register (version debug)

def register(request):
    """
    Vue d'inscription avec connexion automatique et redirection appropriée
    """
    print("\n" + "="*50)
    print("DEBUG REGISTER VIEW")
    print("Méthode:", request.method)
    print("Authentifié:", request.user.is_authenticated)
    print("="*50)
    
    if request.user.is_authenticated:
        print("→ Utilisateur déjà connecté, redirection vers home")
        return redirect('home')
        
    if request.method == 'POST':
        print("\nDonnées POST reçues:")
        for key, value in request.POST.items():
            if 'password' not in key.lower():
                print(f"  {key}: {value}")
        
        form = UserRegisterForm(request.POST)
        
        print("\nFormulaire valide:", form.is_valid())
        
        if not form.is_valid():
            print("\nErreurs du formulaire:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
        
        if form.is_valid():
            try:
                print("\n→ Formulaire valide, création de l'utilisateur...")
                user = form.save(commit=False)
                user.is_active = True
                user.save()
                print(f"→ Utilisateur créé: {user.username} (ID: {user.id})")

                profile = user.profile
                print(f"→ Profil trouvé: {profile}")
                
                # Mise à jour du profil
                profile.user_type = form.cleaned_data['user_type']
                profile.phone = form.cleaned_data.get('phone', '')
                profile.country = form.cleaned_data.get('country', '')
                profile.city = form.cleaned_data.get('city', '')
                profile.company_name = form.cleaned_data.get('company_name', '')
                profile.bio = form.cleaned_data.get('bio', '')
                
                print(f"→ Type d'utilisateur: {profile.user_type}")
                
                if profile.user_type == 'fournisseur':
                    profile.is_active = True
                    profile.is_approved = False
                    profile.save()
                    print("→ Fournisseur - En attente d'approbation")
                    
                    authenticated_user = authenticate(
                        request,
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password1']
                    )
                    print(f"→ Authentification: {'OK' if authenticated_user else 'ÉCHEC'}")
                    
                    if authenticated_user:
                        login(request, authenticated_user)
                        print("→ Connexion réussie, redirection vers supplier-pending")
                        messages.success(request, "✅ Compte fournisseur créé ! En attente de validation.")
                        return redirect('supplier-pending')
                    else:
                        print("→ ÉCHEC de connexion!")
                        messages.error(request, "Erreur de connexion automatique.")
                        return redirect('custom-login')
                        
                else:
                    profile.is_active = True
                    profile.is_approved = True
                    profile.save()
                    print("→ Vendeur - Compte activé")
                    
                    authenticated_user = authenticate(
                        request,
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password1']
                    )
                    print(f"→ Authentification: {'OK' if authenticated_user else 'ÉCHEC'}")
                    
                    if authenticated_user:
                        login(request, authenticated_user)
                        print("→ Connexion réussie, redirection vers home")
                        messages.success(request, f"🎉 Bienvenue {user.username} !")
                        return redirect('home')
                    else:
                        print("→ ÉCHEC de connexion!")
                        messages.error(request, "Erreur de connexion automatique.")
                        return redirect('custom-login')

            except Exception as e:
                print(f"\n❌ ERREUR: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, f"Erreur: {str(e)}")
                if 'user' in locals():
                    try:
                        user.delete()
                        print("→ Utilisateur supprimé (rollback)")
                    except:
                        pass
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Vue principale du profil avec gestion de la mise à jour"""
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '✅ Votre profil a été mis à jour avec succès !')
            return redirect('profile')
        else:
            messages.error(request, '❌ Veuillez corriger les erreurs ci-dessous.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'active_tab': request.GET.get('tab', 'info')
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_update(request):
    """Vue dédiée à la modification du profil"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '✅ Votre profil a été mis à jour avec succès !')
            return redirect('profile')
        else:
            messages.error(request, '❌ Veuillez corriger les erreurs ci-dessous.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user': request.user
    }
    return render(request, 'accounts/profile_update.html', context)


@login_required
@require_POST
def profile_update_api(request):
    """API pour mettre à jour le profil (AJAX) - Dépréciée"""
    return JsonResponse({
        'status': 'error', 
        'message': 'Cette API est dépréciée. Utilisez le formulaire standard.'
    }, status=410)


def public_profile(request, user_id):
    """Vue publique du profil d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    products = []
    requests_list = []
    
    try:
        if user.profile.user_type == 'fournisseur':
            from marketplace.models import Product
            products = Product.objects.filter(supplier=user, is_active=True)
        else:
            from marketplace.models import Request
            requests_list = Request.objects.filter(buyer=user, is_active=True)
    except Exception as e:
        logger.error(f"Erreur chargement profil public: {str(e)}")
    
    context = {
        'profile_user': user,
        'products': products,
        'requests': requests_list
    }
    return render(request, 'accounts/public_profile.html', context)


def custom_login(request):
    """
    Vue de connexion personnalisée avec authentification par email
    Gère les fournisseurs en attente de validation
    """
    
    # Si l'utilisateur est déjà connecté
    if request.user.is_authenticated:
        try:
            # Vérifier le statut du fournisseur
            if hasattr(request.user, 'profile'):
                if request.user.profile.user_type == 'fournisseur':
                    if not request.user.profile.is_approved:
                        return redirect('supplier-pending')
                    return redirect('supplier-dashboard')
        except Exception:
            pass
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('login', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')
        
        # Validation de base
        if not email or not password:
            messages.error(request, '❌ Veuillez remplir tous les champs.')
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
                # Vérifier si le compte fournisseur est approuvé
                if hasattr(authenticated_user, 'profile'):
                    if authenticated_user.profile.user_type == 'fournisseur' and not authenticated_user.profile.is_approved:
                        messages.warning(
                            request, 
                            "⏳ Votre compte fournisseur est en cours de validation. "
                            "Vous recevrez un email dès qu'il sera activé."
                        )
                        return render(request, 'accounts/login.html')
                
                # Connexion réussie
                login(request, authenticated_user)
                
                # Gérer "Se souvenir de moi"
                if not remember:
                    request.session.set_expiry(0)  # Session expire à la fermeture du navigateur
                else:
                    request.session.set_expiry(1209600)  # 2 semaines
                
                messages.success(
                    request, 
                    f'👋 Bienvenue {authenticated_user.username} !'
                )
                
                # Redirection selon le type d'utilisateur
                if hasattr(authenticated_user, 'profile'):
                    if authenticated_user.profile.user_type == 'fournisseur':
                        return redirect('supplier-dashboard')
                
                return redirect('home')
            else:
                messages.error(request, '❌ Mot de passe incorrect.')
                
        except User.DoesNotExist:
            messages.error(request, f'❌ Aucun compte trouvé avec l\'email "{email}".')
            logger.warning(f"Tentative de connexion avec email inexistant: {email}")
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {str(e)}")
            messages.error(request, 'Une erreur est survenue. Veuillez réessayer.')
    
    return render(request, 'accounts/login.html')


def supplier_pending(request):
    """
    Page d'attente pour les fournisseurs en attente de validation
    """
    # Vérifier que l'utilisateur est connecté
    if not request.user.is_authenticated:
        messages.info(request, "Veuillez vous connecter pour accéder à cette page.")
        return redirect('custom-login')
    
    # Vérifier le profil
    try:
        # Si l'utilisateur est approuvé, le rediriger
        if request.user.profile.is_approved:
            if request.user.profile.user_type == 'fournisseur':
                return redirect('supplier-dashboard')
            else:
                return redirect('home')
        
        # Si c'est un vendeur, rediriger vers home
        if request.user.profile.user_type != 'fournisseur':
            return redirect('home')
            
    except Profile.DoesNotExist:
        messages.error(request, "Profil non trouvé. Veuillez contacter le support.")
        return redirect('home')
    except Exception as e:
        logger.error(f"Erreur page attente: {str(e)}")
        return redirect('home')
    
    return render(request, 'accounts/supplier_pending.html')


def custom_logout(request):
    """Vue de déconnexion personnalisée"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'👋 Au revoir {username} ! Vous avez été déconnecté avec succès.')
    else:
        messages.info(request, 'Vous êtes déjà déconnecté.')
    
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
        return JsonResponse({
            'status': 'success', 
            'message': '✅ Mot de passe changé avec succès !'
        })
    else:
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list[0]
        return JsonResponse({
            'status': 'error', 
            'errors': errors
        }, status=400)