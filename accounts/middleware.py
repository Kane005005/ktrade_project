# accounts/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class SupplierApprovalMiddleware:
    """
    Middleware pour vérifier si un fournisseur est approuvé avant d'accéder
    à certaines pages
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si l'utilisateur est connecté
        if request.user.is_authenticated:
            try:
                # Si c'est un fournisseur non approuvé
                if (request.user.profile.user_type == 'fournisseur' and 
                    not request.user.profile.is_approved):
                    
                    # Liste des URLs autorisées pour les fournisseurs non approuvés
                    allowed_urls = [
                        reverse('custom-login'),
                        reverse('custom-logout'),
                        reverse('supplier-pending'),
                        reverse('admin:index'),  # Admin
                        '/accounts/google/login/',  # Google login
                        '/accounts/google/login/callback/',  # Google callback
                    ]
                    
                    # Vérifier si l'URL actuelle est autorisée
                    current_path = request.path
                    if not any(current_path.startswith(url) for url in allowed_urls):
                        messages.warning(
                            request,
                            "Votre compte fournisseur est en attente de validation."
                        )
                        return redirect('supplier-pending')
                        
            except AttributeError:
                # Pas de profil, on laisse passer
                pass
                
        response = self.get_response(request)
        return response