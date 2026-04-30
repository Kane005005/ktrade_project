

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Product, Request, Category, Favorite
from .forms import ProductForm, RequestForm, SearchForm
from accounts.models import Profile

class ProductListView(ListView):
    model = Product
    template_name = 'marketplace/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('supplier', 'category')
        
        # Filtres
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(country_of_origin__icontains=country)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = 'Tous les produits'
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'marketplace/product_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['related_products'] = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(id=product.id)[:4]
        
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user, product=product
            ).exists()
        
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'marketplace/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        form.instance.supplier = self.request.user
        messages.success(self.request, 'Produit ajouté avec succès!')
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.user_type != 'fournisseur':
            messages.error(request, 'Seuls les fournisseurs peuvent ajouter des produits.')
            return redirect('product-list')
        return super().dispatch(request, *args, **kwargs)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'marketplace/product_form.html'
    
    def test_func(self):
        product = self.get_object()
        return self.request.user == product.supplier
    
    def form_valid(self, form):
        messages.success(self.request, 'Produit mis à jour avec succès!')
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product-list')
    
    def test_func(self):
        product = self.get_object()
        return self.request.user == product.supplier
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Produit supprimé avec succès!')
        return super().delete(request, *args, **kwargs)

class RequestListView(ListView):
    model = Request
    template_name = 'marketplace/request_list.html'
    context_object_name = 'requests'
    paginate_by = 12
    
    def get_queryset(self):
        return Request.objects.filter(is_active=True).select_related('buyer', 'category').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = 'Toutes les demandes'
        return context

class RequestDetailView(DetailView):
    model = Request
    template_name = 'marketplace/request_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_obj = self.get_object()
        context['similar_requests'] = Request.objects.filter(
            category=request_obj.category, is_active=True
        ).exclude(id=request_obj.id)[:4]
        return context

class RequestCreateView(LoginRequiredMixin, CreateView):
    model = Request
    form_class = RequestForm
    template_name = 'marketplace/request_form.html'
    success_url = reverse_lazy('request-list')
    
    def form_valid(self, form):
        form.instance.buyer = self.request.user
        messages.success(self.request, 'Demande créée avec succès!')
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.user_type != 'vendeur':
            messages.error(request, 'Seuls les acheteurs peuvent créer des demandes.')
            return redirect('request-list')
        return super().dispatch(request, *args, **kwargs)

class RequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Request
    form_class = RequestForm
    template_name = 'marketplace/request_form.html'
    
    def test_func(self):
        request_obj = self.get_object()
        return self.request.user == request_obj.buyer
    
    def form_valid(self, form):
        messages.success(self.request, 'Demande mise à jour avec succès!')
        return super().form_valid(form)

class RequestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Request
    success_url = reverse_lazy('request-list')
    
    def test_func(self):
        request_obj = self.get_object()
        return self.request.user == request_obj.buyer
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Demande supprimée avec succès!')
        return super().delete(request, *args, **kwargs)

def search_view(request):
    form = SearchForm(request.GET)
    products = Product.objects.filter(is_active=True)
    requests = Request.objects.filter(is_active=True)
    
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        country = form.cleaned_data.get('country')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        user_type = form.cleaned_data.get('user_type')
        
        if q:
            products = products.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
            requests = requests.filter(
                Q(product_name__icontains=q) | Q(description__icontains=q)
            )
        
        if category:
            products = products.filter(category=category)
            requests = requests.filter(category=category)
        
        if country:
            products = products.filter(country_of_origin__icontains=country)
            requests = requests.filter(desired_country__icontains=country)
        
        if min_price:
            products = products.filter(estimated_price__gte=min_price)
            requests = requests.filter(max_budget__gte=min_price)
        
        if max_price:
            products = products.filter(estimated_price__lte=max_price)
            requests = requests.filter(max_budget__lte=max_price)
        
        if user_type == 'fournisseur':
            requests = requests.none()
        elif user_type == 'vendeur':
            products = products.none()
    
    context = {
        'form': form,
        'products': products[:10],
        'requests': requests[:10],
        'query': request.GET.get('q', '')
    }
    return render(request, 'marketplace/search_results.html', context)

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if not created:
        favorite.delete()
        messages.success(request, 'Retiré des favoris')
    else:
        messages.success(request, 'Ajouté aux favoris')
    
    return redirect('product-detail', pk=product_id)

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'marketplace/categories.html', {'categories': categories})

def home(request):
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    latest_requests = Request.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.all()[:6]
    
    context = {
        'latest_products': latest_products,
        'latest_requests': latest_requests,
        'categories': categories,
    }
    return render(request, 'marketplace/home.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q
from .models import Product, Request
from chat.models import Conversation, Message

@login_required
def supplier_dashboard(request):
    """Tableau de bord pour les fournisseurs"""
    
    # Vérifier que l'utilisateur est bien un fournisseur
    if request.user.profile.user_type != 'fournisseur':
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, "Cette page est réservée aux fournisseurs.")
        return redirect('home')
    
    # Statistiques
    products = Product.objects.filter(supplier=request.user)
    products_count = products.filter(is_active=True).count()
    
    # Produits récents
    recent_products = products.order_by('-created_at')[:5]
    
    # Demandes récentes (pour les catégories du fournisseur)
    supplier_categories = products.values_list('category', flat=True).distinct()
    recent_requests = Request.objects.filter(
        category__in=supplier_categories,
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Messages non lus
    unread_messages = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    
    # Calculer le pourcentage de complétion du profil
    profile = request.user.profile
    profile_fields = [
        profile.phone,
        profile.country,
        profile.city,
        profile.bio,
        profile.profile_picture
    ]
    if profile.user_type == 'fournisseur':
        profile_fields.append(profile.company_name)
    
    filled_fields = sum(1 for field in profile_fields if field)
    total_fields = len(profile_fields)
    profile_completion = int((filled_fields / total_fields) * 100)
    
    # Trouver le produit le plus vu (à implémenter avec un champ views)
    top_product = products.order_by('-created_at').first()
    
    context = {
        'products_count': products_count,
        'recent_products': recent_products,
        'recent_requests': recent_requests,
        'unread_messages': unread_messages,
        'profile_completion': profile_completion,
        'top_product': top_product.name if top_product else None,
        'total_orders': 0,  # À implémenter avec un modèle Order
        'interested_buyers': 0,  # À implémenter
    }
    
    return render(request, 'marketplace/supplier_dashboard.html', context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Request
from chat.models import Conversation, Message, Notification

@login_required
@login_required
@require_POST
def make_offer(request, request_id):
    """Faire une offre sur une demande d'achat"""
    
    # Vérifier que l'utilisateur est un fournisseur
    if request.user.profile.user_type != 'fournisseur':
        messages.error(request, "Seuls les fournisseurs peuvent faire des offres.")
        return redirect('request-detail', pk=request_id)
    
    # Récupérer la demande
    purchase_request = get_object_or_404(Request, id=request_id, is_active=True)
    
    # Récupérer les données du formulaire
    price = request.POST.get('price')
    quantity = request.POST.get('quantity')
    message = request.POST.get('message', '')
    
    # Valider les données
    if not price or not quantity:
        messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        return redirect('request-detail', pk=request_id)
    
    try:
        price = float(price)
        quantity = int(quantity)
        
        if price <= 0 or quantity <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Veuillez entrer des valeurs valides.")
        return redirect('request-detail', pk=request_id)
    
    # Créer ou récupérer une conversation
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=purchase_request.buyer
    ).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, purchase_request.buyer)
    
    # Créer le message avec l'offre
    offer_message = f"📦 **OFFRE**\n\n"
    offer_message += f"Produit: {purchase_request.product_name}\n"
    offer_message += f"Prix proposé: {price} {purchase_request.budget_currency}\n"
    offer_message += f"Quantité disponible: {quantity}\n\n"
    offer_message += f"Message: {message}"
    
    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=offer_message
    )
    
    # ✅ CORRECTION ICI - Utiliser 'or' au lieu de '|default:'
    company_name = request.user.profile.company_name or request.user.username
    
    # Créer une notification pour l'acheteur
    Notification.objects.create(
        recipient=purchase_request.buyer,
        sender=request.user,
        notification_type='offer',
        content=f"Nouvelle offre de {company_name} pour {purchase_request.product_name}",
        link=f"/chat/conversation/{conversation.id}/"
    )
    
    messages.success(request, "Votre offre a été envoyée avec succès!")
    return redirect('chat-detail', conversation_id=conversation.id)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Request
from chat.models import Notification

@login_required
@require_POST
def report_request(request, request_id):
    """Signaler une demande inappropriée"""
    
    # Récupérer la demande
    purchase_request = get_object_or_404(Request, id=request_id)
    
    # Empêcher de signaler sa propre demande
    if purchase_request.buyer == request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'Vous ne pouvez pas signaler votre propre demande.'
        }, status=400)
    
    # Vérifier si l'utilisateur a déjà signalé cette demande
    # (Vous pouvez créer un modèle Report pour suivre les signalements)
    
    # Créer une notification pour l'administrateur (optionnel)
    # Pour l'instant, on peut juste logger le signalement
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Demande #{request_id} signalée par {request.user.username} (ID: {request.user.id})")
    
    # Envoyer un email à l'admin (optionnel)
    # send_mail(...)
    
    # Créer une notification (optionnel)
    # Notification.objects.create(...)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Demande signalée. Merci de votre aide !'
    })