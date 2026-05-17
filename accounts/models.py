# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Modèle étendu pour le profil utilisateur"""
    
    class UserType(models.TextChoices):
        FOURNISSEUR = 'fournisseur', 'Fournisseur'
        VENDEUR = 'vendeur', 'Vendeur'
    
    # Relation OneToOne avec User
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Type d'utilisateur
    user_type = models.CharField(
        max_length=20, 
        choices=UserType.choices, 
        default=UserType.VENDEUR
    )
    
    # Informations de contact
    phone = models.CharField(max_length=20, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    
    # Informations professionnelles
    company_name = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        help_text="Nom de l'entreprise (obligatoire pour les fournisseurs)"
    )
    bio = models.TextField(max_length=500, blank=True, default='')
    
    # Photo de profil
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True
    )
    
    # Statuts de validation
    is_active = models.BooleanField(
        default=True,
        help_text="Profil actif/inactif"
    )
    is_approved = models.BooleanField(
        default=True,
        help_text="Approuvé par l'administration (False pour nouveaux fournisseurs)"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.get_user_type_display()}"

    def get_approval_status(self):
        """Retourne le statut de validation pour l'admin"""
        if self.user_type == self.UserType.FOURNISSEUR:
            if self.is_approved:
                return "✅ Approuvé"
            return "⏳ En attente"
        return "N/A"


# Signals pour créer/mettre à jour le profil automatiquement
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil quand un utilisateur est créé"""
    if created:
        # Définir is_approved par défaut selon le type
        # Mais comme on ne connaît pas encore le type, on met True
        # Le type sera défini lors de l'inscription
        Profile.objects.get_or_create(
            user=instance,
            defaults={
                'is_active': True,
                'is_approved': True
            }
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil quand l'utilisateur est sauvegardé"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Créer le profil s'il n'existe pas (ne devrait pas arriver grâce au signal create)
        Profile.objects.create(user=instance)