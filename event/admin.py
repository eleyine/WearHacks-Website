from django.contrib import admin
from event.models import Person, Sponsor, Workshop, Prize, PrizePerk

class PersonAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'
    fieldsets = (
        ('General Info', {
            'fields': (
                ('first_name', 'last_name'),
                'category',
                'company',
                'gender', 
                'rank',
                )
        }),
        ('About', {
            'fields': (
                'profile_pic',
                'role',
                'biography',
                )
        }),
        ('Contact Info', {
            'fields': (
                'email',
                'telephone',
                )
        }),
        ('Social Media', {
            'fields': (
                'linkedin',
                'website',
                'twitter',
                'github',
                'facebook',
                )
        }),
        )
    list_display = (
            'updated_at',
            'category',
            'rank',
            'profile_pic',
            'full_name',
            'company',
            'role',
            'email', 
            'password',
            'has_telephone',
            'has_linkedin',
            'has_website',
            'has_twitter',
            'has_github',
            'has_facebook',           
        )
    # list_editable = ('staff_comments',)
    search_fields = ['category', 'company', 'email', 'first_name', 'last_name']
    list_filter = ('category', 'company', 'gender')
    list_display_links = ('full_name',)

admin.site.register(Person, PersonAdmin)
admin.site.register(Sponsor)
admin.site.register(Workshop)
admin.site.register(Prize)
admin.site.register(PrizePerk)

