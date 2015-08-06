from django.contrib import admin
from registration.models import Registration, ChargeAttempt

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
        ('Legal Info', {
            'classes': ('collapse',),
            'fields': (
                ('has_read_code_of_conduct', 'has_read_waiver'),
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
            'needs_to_be_checked',
            'staff_comments',
        )
    # list_editable = ('staff_comments',)
    search_fields = ['order_id', 'email', 'first_name', 'last_name']
    list_filter = ('charge__is_captured', 'is_student', 'has_attended', 'is_email_sent', )
    list_display_links = ('order_id',)

admin.site.register(Registration, RegistrationAdmin)
admin.site.register(ChargeAttempt)

