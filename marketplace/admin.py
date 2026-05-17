# marketplace/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Product, Request, Favorite


# ============================================
# CATEGORY ADMIN
# ============================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_display', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def icon_display(self, obj):
        if obj.icon:
            return format_html('<i class="fas {}"></i> {}', obj.icon, obj.icon)
        return "-"
    icon_display.short_description = 'Icône'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Nb produits'


# ============================================
# PRODUCT ADMIN
# ============================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier_link', 'category', 'estimated_price', 'price_currency', 
                   'quantity_available', 'country_of_origin', 'image_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'price_currency', 'country_of_origin', 'created_at')
    search_fields = ('name', 'description', 'supplier__username', 'supplier__email')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('supplier', 'name', 'category', 'is_active')
        }),
        ('Prix et quantité', {
            'fields': ('estimated_price', 'price_currency', 'quantity_available')
        }),
        ('Description', {
            'fields': ('description', 'country_of_origin'),
            'classes': ('wide',),
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def supplier_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.supplier.id])
        return format_html('<a href="{}">{}</a>', url, obj.supplier.username)
    supplier_link.short_description = 'Fournisseur'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', 
                              obj.image.url)
        return "Pas d'image"
    image_preview.short_description = 'Aperçu'
    
    actions = ['activate_products', 'deactivate_products']
    
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} produits activés avec succès.")
    activate_products.short_description = "Activer les produits sélectionnés"
    
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} produits désactivés avec succès.")
    deactivate_products.short_description = "Désactiver les produits sélectionnés"


# ============================================
# REQUEST ADMIN
# ============================================
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'buyer_link', 'category', 'desired_quantity', 
                   'desired_country', 'max_budget', 'budget_currency', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'budget_currency', 'desired_country', 'created_at')
    search_fields = ('product_name', 'description', 'buyer__username', 'buyer__email')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('buyer', 'product_name', 'category', 'is_active')
        }),
        ('Quantité et budget', {
            'fields': ('desired_quantity', 'max_budget', 'budget_currency')
        }),
        ('Localisation', {
            'fields': ('desired_country',)
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def buyer_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.buyer.id])
        return format_html('<a href="{}">{}</a>', url, obj.buyer.username)
    buyer_link.short_description = 'Acheteur'
    
    actions = ['activate_requests', 'deactivate_requests']
    
    def activate_requests(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} demandes activées avec succès.")
    activate_requests.short_description = "Activer les demandes sélectionnées"
    
    def deactivate_requests(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} demandes désactivées avec succès.")
    deactivate_requests.short_description = "Désactiver les demandes sélectionnées"


# ============================================
# FAVORITE ADMIN
# ============================================
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    
    def item_display(self, obj):
        if obj.product:
            url = reverse('admin:marketplace_product_change', args=[obj.product.id])
            return format_html('Produit: <a href="{}">{}</a>', url, obj.product.name)
        elif obj.request:
            url = reverse('admin:marketplace_request_change', args=[obj.request.id])
            return format_html('Demande: <a href="{}">{}</a>', url, obj.request.product_name)
        return "-"
    item_display.short_description = 'Élément favori'