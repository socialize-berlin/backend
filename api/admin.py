from django.contrib import admin
from .models import Walk, WalkAttendee, User, Message, Connection, ConnectionMessage, PasswordReset, Survey, SurveyOption

@admin.register(Walk)
class WalkAdmin(admin.ModelAdmin):
    fields = ['author', 'date', 'time', 'lat', 'lng', 'message']
    list_display = ('author', 'date', 'time', 'lat', 'lng', 'created')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ['first_name', 'last_name', 'email', 'username', 'avatar', 'lat', 'lng', 'is_confirmed', 'headline', 'introduction']
    list_display = ('email', 'first_name', 'last_name', 'is_confirmed')

@admin.register(WalkAttendee)
class WalkAttendeeAdmin(admin.ModelAdmin):
    fields = ['walk', 'user', 'accepted']
    list_display = ('walk', 'user', 'accepted')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    fields = ['name', 'email', 'message']
    list_display = ('name', 'email', 'message', 'created')


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    fields = ['author', 'invitee', 'status']
    list_display = ('author', 'invitee', 'status', 'created')

@admin.register(ConnectionMessage)
class ConnectionMessageAdmin(admin.ModelAdmin):
    fields = ['connection', 'author', 'is_seen', 'is_notification_sent']
    list_display = ('connection', 'author', 'is_seen', 'is_notification_sent', 'created')

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    fields = ['user', 'used']
    list_display = ('user', 'token', 'used', 'created')

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    fields = ['name', 'is_featured']
    list_display = ('name', 'is_featured', 'created')


@admin.register(SurveyOption)
class SurveyOptionAdmin(admin.ModelAdmin):
    fields = ['name', 'survey']
    list_display = ('name', 'survey', 'votes', 'created')
