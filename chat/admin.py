from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message, Notification

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('sender', 'content', 'translated_content', 'is_read', 'timestamp')
    can_delete = False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'participants_list', 'message_count', 'last_message_time', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('participants__username', 'participants__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]
    
    fieldsets = (
        ('Informations', {
            'fields': ('participants',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    filter_horizontal = ('participants',)
    
    def participants_list(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    participants_list.short_description = 'Participants'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def last_message_time(self, obj):
        last_msg = obj.messages.last()
        return last_msg.timestamp if last_msg else "-"
    last_message_time.short_description = 'Dernier message'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation_link', 'sender_link', 'content_preview', 
                   'has_translation', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp', 'translation_language')
    search_fields = ('content', 'sender__username', 'sender__email')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        ('Conversation', {
            'fields': ('conversation', 'sender')
        }),
        ('Contenu', {
            'fields': ('content', 'translated_content', 'translation_language'),
            'classes': ('wide',),
        }),
        ('Statut', {
            'fields': ('is_read', 'timestamp'),
        }),
    )
    
    def conversation_link(self, obj):
        return format_html('<a href="/admin/chat/conversation/{}/change/">Conversation #{}</a>', 
                          obj.conversation.id, obj.conversation.id)
    conversation_link.short_description = 'Conversation'
    
    def sender_link(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', 
                          obj.sender.id, obj.sender.username)
    sender_link.short_description = 'Expéditeur'
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Aperçu'
    
    def has_translation(self, obj):
        if obj.translated_content:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
    has_translation.short_description = 'Traduit'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient_link', 'sender_link', 'notification_type', 'content_preview', 
                   'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'content')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Destinataires', {
            'fields': ('recipient', 'sender')
        }),
        ('Notification', {
            'fields': ('notification_type', 'content', 'link'),
        }),
        ('Statut', {
            'fields': ('is_read', 'created_at'),
        }),
    )
    
    def recipient_link(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', 
                          obj.recipient.id, obj.recipient.username)
    recipient_link.short_description = 'Destinataire'
    
    def sender_link(self, obj):
        if obj.sender:
            return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', 
                              obj.sender.id, obj.sender.username)
        return "-"
    sender_link.short_description = 'Expéditeur'
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Aperçu'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications marquées comme lues.")
    mark_as_read.short_description = "Marquer comme lues"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} notifications marquées comme non lues.")
    mark_as_unread.short_description = "Marquer comme non lues"