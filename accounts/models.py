from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserType(models.TextChoices):
    FOURNISSEUR = 'fournisseur', 'Fournisseur'
    VENDEUR = 'vendeur', 'Vendeur'

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    class UserType(models.TextChoices):
        FOURNISSEUR = 'fournisseur', 'Fournisseur'
        VENDEUR = 'vendeur', 'Vendeur'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.VENDEUR)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, help_text="Nom de l'entreprise (pour les fournisseurs)")
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.user_type}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)