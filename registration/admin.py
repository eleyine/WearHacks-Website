from django.contrib import admin
from registration.models import Registration, ChargeAttempt, Challenge

class RegistrationAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'
    fieldsets = (
        ('General Info', {
            'fields': (
                ('first_name', 'last_name'),
                ('gender', 'email'),
                )
        }),
        ('Order Info', {
            'fields': (
                'order_id',
                'charge',
                'ticket_description',
                ('ticket_file', 'qrcode_file'),
                'is_email_sent',
                )
        }),
        ('Sponsor Info', {
            'fields': (
                ('github', 'linkedin',),
                ('resume',),
                )
        }),
        ('Event Logistics', {
            'classes': ('collapse',),
            'fields': (
                'tshirt_size', 
                'food_restrictions', 
                'preferred_language',
                )
        }),
        ('Challenge', {
            'classes': ('collapse',),
            'fields': (
                ('has_solved_challenge', 'solved_challenge'),
                )
        }),
        ('Legal Info', {
            'classes': ('collapse',),
            'fields': (
                ('has_read_conditions',),
                )
        }),
        (None, {
            'fields' : ('staff_comments',)
        })
        )
    list_display = (
            'updated_at',
            'order_id',
            'is_charged',
            'full_name',
            'email',
            'charge',
            'has_attended',
            'is_email_sent',
            'is_student',
            'has_solved_challenge',
            'solved_challenge',
            'needs_to_be_checked',
            'staff_comments',
        )
    # list_editable = ('staff_comments',)
    search_fields = ['order_id', 'email', 'first_name', 'last_name']
    list_filter = ('has_solved_challenge', 'charge__is_captured', 'is_student', 'has_attended', 'is_email_sent', )
    list_display_links = ('order_id',)

class ChallengeAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'
    fieldsets = (
        ('Challenge Strings', {
            'fields': (
                'encrypted_message',
                'decrypted_message'
                )
        }),
        (None,{
            'fields': (
                'solved',
                'language'
                )
        }),
    )
    list_display = (
            'updated_at',
            'solvers',
            'solved',
            'language',
            'decrypted_message',
            'encrypted_message',
        )
    # list_editable = ('staff_comments',)
    search_fields = ['decrypted_message']
    list_filter = ('solved', 'language', )
    list_display_links = ('decrypted_message',)

admin.site.register(Registration, RegistrationAdmin)
admin.site.register(ChargeAttempt)
admin.site.register(Challenge, ChallengeAdmin)

