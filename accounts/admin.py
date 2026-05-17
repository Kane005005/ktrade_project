# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Type de compte', {
            'fields': ('user_type', 'is_active', 'is_approved')
        }),
        ('Informations personnelles', {
            'fields': ('phone', 'country', 'city', 'profile_picture')
        }),
        ('Informations professionnelles', {
            'fields': ('company_name', 'bio'),
            'classes': ('wide',),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'get_user_type', 'get_approval_status', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 
                  'profile__user_type', 'profile__is_approved')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__company_name')
    
    actions = ['approve_suppliers']
    
    def get_user_type(self, obj):
        """Retourne le type d'utilisateur sous forme de texte simple"""
        try:
            return obj.profile.get_user_type_display()
        except Profile.DoesNotExist:
            return 'Non défini'
    get_user_type.short_description = 'Type'
    get_user_type.admin_order_field = 'profile__user_type'
    
    def get_approval_status(self, obj):
        """Retourne le statut d'approbation - CORRIGÉ"""
        try:
            if obj.profile.user_type == 'fournisseur':
                if obj.profile.is_approved:
                    return format_html(
                        '<span style="color: green;">{}</span>',
                        '✓ Approuvé'
                    )
                else:
                    return format_html(
                        '<span style="color: orange;">{}</span>',
                        '⏳ En attente'
                    )
            return format_html('<span style="color: blue;">{}</span>', 'N/A')
        except Profile.DoesNotExist:
            return format_html('<span>{}</span>', '-')
    get_approval_status.short_description = 'Statut validation'
    
    def approve_suppliers(self, request, queryset):
        """Approuver les fournisseurs sélectionnés"""
        count = 0
        for user in queryset:
            try:
                if user.profile.user_type == 'fournisseur' and not user.profile.is_approved:
                    user.profile.is_approved = True
                    user.profile.is_active = True
                    user.profile.save()
                    count += 1
            except Profile.DoesNotExist:
                pass
        self.message_user(request, '{} fournisseur(s) approuvé(s) avec succès.'.format(count))
    approve_suppliers.short_description = "Approuver les fournisseurs sélectionnés"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'user_type', 'company_name', 'country', 'city', 
                   'get_approval_status', 'created_at')
    list_filter = ('user_type', 'is_approved', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'user_type', 'is_active', 'is_approved')
        }),
        ('Contact', {
            'fields': ('phone', 'country', 'city', 'profile_picture')
        }),
        ('Professionnel', {
            'fields': ('company_name', 'bio'),
            'classes': ('wide',),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['approve_profiles', 'unapprove_profiles']
    
    def user_link(self, obj):
        """Lien vers l'utilisateur - CORRIGÉ"""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Utilisateur'
    user_link.admin_order_field = 'user__username'
    
    def get_approval_status(self, obj):
        """Statut d'approbation - CORRIGÉ"""
        if obj.user_type == 'fournisseur':
            if obj.is_approved:
                return format_html(
                    '<span style="color: green;">{}</span>',
                    '✓ Approuvé'
                )
            return format_html(
                '<span style="color: orange;">{}</span>',
                '⏳ En attente'
            )
        return format_html('<span style="color: blue;">{}</span>', 'N/A')
    get_approval_status.short_description = 'Statut'
    get_approval_status.admin_order_field = 'is_approved'
    
    def approve_profiles(self, request, queryset):
        """Approuver les profils"""
        updated = queryset.update(is_approved=True, is_active=True)
        self.message_user(request, '{} profil(s) approuvé(s).'.format(updated))
    approve_profiles.short_description = "Approuver les profils sélectionnés"
    
    def unapprove_profiles(self, request, queryset):
        """Désapprouver les profils"""
        updated = queryset.update(is_approved=False, is_active=False)
        self.message_user(request, '{} profil(s) désapprouvé(s).'.format(updated))
    unapprove_profiles.short_description = "Désapprouver les profils sélectionnés"


# Désinscrire l'admin User par défaut et réinscrire avec notre version personnalisée
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)