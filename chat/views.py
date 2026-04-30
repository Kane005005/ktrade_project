from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Q, Count
from .models import Conversation, Message, Notification
import json
import requests

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Conversation, Message

@login_required
def chat_list(request):
    """Liste des conversations de l'utilisateur"""
    
    # Récupérer toutes les conversations de l'utilisateur
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
    ).order_by('-updated_at')
    
    # Debug : Afficher dans la console
    print(f"Nombre de conversations trouvées : {conversations.count()}")
    for conv in conversations:
        other = conv.get_other_participant(request.user)
        print(f"Conversation {conv.id} avec {other.username if other else 'Inconnu'}")
    
    context = {
        'conversations': conversations,
    }
    
    return render(request, 'chat/chat_list.html', context)

@login_required
def chat_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    other_user = conversation.get_other_participant(request.user)
    
    # Marquer les messages comme lus
    unread_messages = conversation.messages.filter(~Q(sender=request.user), is_read=False)
    for message in unread_messages:
        message.mark_as_read()
    
    # Créer une notification de lecture
    if unread_messages.exists():
        pass  # La logique de notification sera ajoutée plus tard
    
    context = {
        'conversation': conversation,
        'other_user': other_user,
        'messages': conversation.messages.all()
    }
    return render(request, 'chat/chat_detail.html', context)

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, "Vous ne pouvez pas discuter avec vous-même")
        return redirect('chat-list')
    
    # Vérifier si une conversation existe déjà
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
        
        # Message de bienvenue automatique
        welcome_message = f"Conversation démarrée avec {other_user.username}"
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=welcome_message
        )
        
        # Créer une notification pour l'autre utilisateur
        Notification.objects.create(
            recipient=other_user,
            sender=request.user,
            notification_type='message',
            content=f"{request.user.username} a démarré une conversation avec vous",
            link=f'/chat/conversation/{conversation.id}/'
        )
    
    return redirect('chat-detail', conversation_id=conversation.id)

@login_required
def get_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    last_id = request.GET.get('last_id', 0)
    
    messages_qs = conversation.messages.filter(id__gt=last_id)
    
    messages_data = []
    for msg in messages_qs:
        messages_data.append({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.username,
            'content': msg.content,
            'translated_content': msg.translated_content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_read': msg.is_read,
            'is_mine': msg.sender == request.user
        })
    
    return JsonResponse({'messages': messages_data, 'count': len(messages_data)})

@login_required
@require_POST
def send_message(request):
    data = json.loads(request.body)
    conversation_id = data.get('conversation_id')
    content = data.get('content')
    
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Traduire le message si nécessaire
    translated_content = None
    target_language = data.get('target_language', 'fr')
    
    if target_language != 'fr':  # Si la cible n'est pas le français
        translated_content = translate_text(content, target_language)
    
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content,
        translated_content=translated_content,
        translation_language=target_language if translated_content else None
    )
    
    # Mettre à jour le timestamp de la conversation
    conversation.save()
    
    # Créer une notification pour les autres participants
    other_user = conversation.get_other_participant(request.user)
    if other_user:
        Notification.objects.create(
            recipient=other_user,
            sender=request.user,
            notification_type='message',
            content=f"Nouveau message de {request.user.username}",
            link=f'/chat/conversation/{conversation.id}/'
        )
    
    return JsonResponse({
        'id': message.id,
        'content': message.content,
        'translated_content': message.translated_content,
        'timestamp': message.timestamp.strftime('%H:%M')
    })

@login_required
@require_POST
def mark_as_read(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        message.mark_as_read()
    return JsonResponse({'status': 'ok'})

@login_required
def notifications(request):
    notifications_list = request.user.notifications.all()
    unread_count = notifications_list.filter(is_read=False).count()
    
    context = {
        'notifications': notifications_list,
        'unread_count': unread_count
    }
    return render(request, 'chat/notifications.html', context)

@login_required
@require_POST
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

# Fonction de traduction (à améliorer avec une vraie API)
def translate_text(text, target_language):
    """
    Traduit un texte en utilisant une API de traduction
    Pour l'instant, simulation, à remplacer par une vraie API
    """
    try:
        # Simulation pour le développement
        # À remplacer par un appel API réel (Google Translate, DeepL, etc.)
        translations = {
            'en': f"[EN] {text}",
            'es': f"[ES] {text}",
            'ar': f"[AR] {text}",
            'zh': f"[ZH] {text}"
        }
        return translations.get(target_language, text)
    except Exception as e:
        print(f"Erreur de traduction: {e}")
        return text
    

