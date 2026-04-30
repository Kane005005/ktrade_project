from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {', '.join([p.username for p in self.participants.all()])}"
    
    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()
    
    def last_message(self):
        return self.messages.order_by('-timestamp').first()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    translated_content = models.TextField(blank=True, null=True)
    translation_language = models.CharField(max_length=10, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message de {self.sender.username} à {self.timestamp}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('message', 'Nouveau message'),
        ('offer', 'Nouvelle offre'),
        ('favorite', 'Favori'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification pour {self.recipient.username}: {self.content[:50]}"