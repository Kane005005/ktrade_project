from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Type de compte', {
            'fields': ('user_type',)
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
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__user_type')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__company_name')
    
    def get_user_type(self, obj):
        try:
            return obj.profile.get_user_type_display()
        except Profile.DoesNotExist:
            return 'Non défini'
    get_user_type.short_description = 'Type'
    get_user_type.admin_order_field = 'profile__user_type'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'company_name', 'country', 'city', 'created_at')
    list_filter = ('user_type', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'user_type')
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

# Désinscrire l'admin User par défaut et réinscrire avec notre version personnalisée
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)