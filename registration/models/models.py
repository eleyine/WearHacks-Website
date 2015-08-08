from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as __
from django.conf import settings

from django.core.validators import RegexValidator#, URLValidator
from django.core.exceptions import ValidationError

from django.core.urlresolvers import reverse
from django.db.models import permalink

from registration.models.helpers import *

class ChargeAttempt(models.Model):
    email = models.EmailField()
    charge_id = models.CharField(max_length=27)
    amount = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    # optional fields
    hacker = models.CharField(max_length=200, default='Unknown')
    is_livemode = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    is_captured = models.BooleanField(default=False)

    status = models.CharField(max_length=100, default='No Status')
    source_id = models.CharField(max_length=29)

    # error logging (optional)
    failure_message = models.CharField(default='No Error', max_length=200,
        help_text='Charge object failure message', blank=True)
    failure_code = models.CharField(default='200', max_length=200, 
        help_text='Charge object failure code', blank=True)
    error_http_status = models.CharField(default='200', max_length=4, blank=True)
    error_type = models.CharField(default='None', max_length=200,
        help_text='The type of error returned. Can be invalid_request_error, api_error, or card_error', blank=True)
    error_code = models.CharField(default='None', max_length=200,
        help_text='For card errors, a short string from amongst those listed on the right describing the kind of card error that occurred.', blank=True)
    error_param = models.CharField(default='None', max_length=200,
        help_text='The parameter the error relates to if the error is parameter-specific.', blank=True)
    error_message = models.CharField(default='None', max_length=300,
        help_text='A human-readable message giving more details about the error.', blank=True)
    SERVER_MESSAGE_MAX_LENGTH = 300
    server_message = models.TextField(default='None', max_length=SERVER_MESSAGE_MAX_LENGTH,
        help_text='Message detailing internal server errors for debugging purposes', blank=True)


    def save_server_message(self, messages, exception=None):
        try:
            print 'Saving message to server...'
            server_message = ''
            if self.server_message:
                messages = [self.server_message] + list(messages)
            if exception:
                server_message = '%s (%s)' % ('\n> '.join(messages), str(exception)[:100])
            else:
                server_message = '\n> '.join(messages)
            n = ChargeAttempt.SERVER_MESSAGE_MAX_LENGTH
            if len(server_message) > n:
                self.server_message = "...%s" % (server_message[-(n-3):])
            self.save()
        except Exception, e:
            print 'ERROR: Could not save server message %s to charge attempt %s (%s)' % (
                    self.server_message, self, str(e))

    @property
    def registration(self):
        qs = Registration.objects.filter(charge=self)
        if qs.exists():
            return qs.first()
        else:
            return None    

    class Meta:
        ordering = ('-created_at',)

    def __unicode__(self):
        if self.registration and self.pk:
            return 'Attempt #%i by %s %s' % (self.pk, self.registration.first_name,
                self.registration.last_name)
        else:
            if self.pk:
                return 'Attempt #%i by %s' % (self.pk, self.hacker)
            else:            
                return 'Attempt by %s' % (self.hacker)

class Registration(models.Model):
    import re
    alpha = RegexValidator(regex=re.compile(r'^[\w\s]*$', flags=re.UNICODE), message=_('Only letters are allowed.'))

    first_name = models.CharField(max_length=20, validators=[alpha], 
        verbose_name=_('first name'))
    last_name = models.CharField(max_length=20, validators=[alpha], 
        verbose_name=_('last name'))
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        # Translators: Gender information
        ('N', _('Other / I prefer not to disclose')),
    )
    gender = models.CharField(max_length=20, 
        choices=GENDER_CHOICES, 
        # default=GENDER_CHOICES[0][0],
        verbose_name=_('gender')
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # student-specific
    is_student = models.BooleanField(default=False, verbose_name=_("Are you a student?"))
    school = models.CharField(max_length=100, blank=True, 
        verbose_name=_("Where do/did you go to school?"), validators=[alpha])

    # contact
    email = models.EmailField(verbose_name=_('email'))
    github = models.URLField(max_length=100, blank=True)
    linkedin = models.URLField(max_length=100, blank=True)

    # misc
    food_restrictions = models.TextField(max_length=100, default="None",
        verbose_name=_("Do you have any allergies or food restrictions?"))
    TSHIRT_SIZE_CHOICES = (
        # Translators: T-shirt sizes
        ('S', _('Small')),
        ('M', _('Medium')),
        ('L', _('Large')),
        ('XL', _('X-Large')),
    )
    tshirt_size = models.CharField(max_length=20, 
        choices=TSHIRT_SIZE_CHOICES,
        verbose_name=_('T-Shirt size')
        )
    is_returning = models.BooleanField(default=False, verbose_name=_("Did you attend last year's event?"))
    is_first_time_hacker = models.BooleanField(default=False, verbose_name=_("Is this your first hackathon?"))
    preferred_language = models.CharField(max_length=2, 
        choices=settings.LANGUAGES, 
        default=settings.LANGUAGE_CODE)
    # files
    RESUME_HELP_TEXT = "Not required but this might reach our sponsors for targeted employment opportunities."
    MAX_UPLOAD_SIZE=2621440 # 2.5MB
    resume = models.FileField(upload_to=get_resume_filename, blank=True, 
        verbose_name = _('resume'),
        help_text = __("Help text for resume field", RESUME_HELP_TEXT),
    )
    # has_read_code_of_conduct = models.BooleanField(default=False, 
    #     verbose_name = _('I have read the <a href="#" target="_blank">Code of Conduct.</a>'),
    #     validators = [validate_true])
    # WAIVER_HELP_TEXT = "Not required but it will save us some time during registration."
    # waiver = models.FileField(upload_to=get_waiver_filename, blank=True,
    #     help_text = __("Help text for waiver field", WAIVER_HELP_TEXT),
    #     verbose_name = _('waiver'),
    # )
    # has_read_waiver = models.BooleanField(default=False, 
    #     verbose_name = _('I have read the <a href="#" target="_blank">Waiver.</a>'),
    #     validators = [validate_true])
    has_read_conditions = models.BooleanField(default=False, 
        validators = [validate_true])

    is_email_sent = models.BooleanField(
        default=False,
        verbose_name= 'Was the confirmation email sent?',
    )

    # Ticket Info
    charge = models.ForeignKey('ChargeAttempt', blank=True, null=True) #default=1)

    is_early_bird = models.BooleanField(default=False)

    TICKET_FULL_PRICE = 2000 # in cents
    ticket_price = models.SmallIntegerField(default=0)
    TICKET_DESCRIPTION_CHOICES = (
        # Translators: Ticket descriptions
        ('N', _('No ticket yet')),
        ('CR', _('Turing Ticket')),
        ('CS', _('Turing Student Ticket')),
        ('R', _('Regular Ticket')),
        ('S', _('Student Ticket')),
        ('ER', _('Early Bird Ticket')),
        ('ES', _('Early Bird Student Ticket')),
        )
    ticket_description = models.CharField(default=TICKET_DESCRIPTION_CHOICES[0][0], 
        choices=TICKET_DESCRIPTION_CHOICES, max_length=2)
    ticket_file = models.FileField(upload_to=get_ticket_filename, blank=True)
    qrcode_file = models.FileField(upload_to=get_qrcode_filename, blank=True, storage=OverwriteStorage())

    # Logistics
    ORDER_ID_MAX_LENGTH = 6
    order_id = models.CharField(default='xxx', max_length=ORDER_ID_MAX_LENGTH)

    has_attended = models.BooleanField(default=False)
    staff_comments = models.TextField(max_length=100, default="No comments",
        help_text='Log anything to do with this registration here.',
        blank=True)

    # Challenge
    has_solved_challenge = models.BooleanField(default=False)
    solved_challenge = models.ForeignKey('Challenge', null=True)

    @property
    def has_submitted_waiver(self):
        print "waiver", self.waiver
        print bool(self.waiver)
        print 'name', self.waiver.name
        return bool(self.waiver)

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    full_name.admin_order_field = 'last_name'

    def needs_to_be_checked(self):
        result = False
        if self.is_email_sent and self.charge and \
            not self.charge.is_captured:
            result = True
        return result


    def is_charged(self):
        return bool(self.charge) and self.charge.is_captured
    
    @staticmethod
    def get_ticket_info(registration=None, is_early_bird=False, is_student=False,
        has_solved_challenge=False):
        from datetime import datetime

        if registration:
            is_early_bird = registration.is_early_bird
            is_student = registration.is_student
            has_solved_challenge = registration.has_solved_challenge

        # ticket price
        # full_price = Registration.TICKET_FULL_PRICE
        # ratio_to_pay = 0.5 if is_early_bird else 1
        # ratio_to_pay = ratio_to_pay * 0.5 if is_student else ratio_to_pay
        # price = full_price * ratio_to_pay
        
        if has_solved_challenge:
            price = 0
        else:
            price = 15 if is_student else 25
        price = price * 100 # in cents

        # ticket description
        choices = dict(Registration.TICKET_DESCRIPTION_CHOICES)
        description = '' #'E' if is_early_bird else ''
        description += 'C' if has_solved_challenge else ''
        description += 'S' if is_student else 'R'
        return (description, price)

    @staticmethod
    def generate_order_id():
        from random import randint
        n, generated, order_id = Registration.ORDER_ID_MAX_LENGTH, False, 'xxx'
        while not generated:
            order_id = ''.join(["%s" % randint(0, 9) for num in range(0, n)])
            if not Registration.objects.filter(order_id=order_id).exists():
                generated = True
        return order_id

    def get_confirmation_url(self):
        """
        Staff-only url to confirm registration
        """
        url = reverse("confirm-registration", kwargs={'order_id': str(self.order_id)})
        full_url = ''.join([settings.HTTP_PREFIX, settings.HOSTS[0], url])
        return full_url 

    def get_qrcode_url(self):
        """
        Access hacker mobile ticket
        """
        url = reverse("qrcode", kwargs={'order_id': str(self.order_id)})
        full_url = ''.join([settings.HTTP_PREFIX, settings.HOSTS[0], url])
        return full_url 

    def get_absolute_url(self):
        return reverse("confirmation_email", kwargs={'order_id': str(self.order_id)})


    class Meta:
        ordering = ('-updated_at', 'last_name', 'first_name',)

    def __unicode__(self):
        if self.pk:
            return '{0} {1} (#{2})'.format(self.first_name, self.last_name, self.pk)
        else:
            return '{0} {1} (Not saved)'.format(self.first_name, self.last_name)

class Challenge(models.Model):
    encrypted_message = models.CharField(max_length=200)
    decrypted_message = models.CharField(max_length=200)
    solved = models.BooleanField(default=False)
    language = models.CharField(max_length=2, 
        choices=settings.LANGUAGES, 
        default=settings.LANGUAGE_CODE)
    updated_at = models.DateTimeField(auto_now=True)

    MAX_NUM_STUDENT = 50
    MAX_NUM_NON_STUDENT = 50

    @property
    def solver(self):
        qs = Registration.objects.filter(solved_challenge__id=self.id)
        print qs
        if qs.exists():
            return qs.first().full_name
        else:
            return 'No one yet'

    @staticmethod
    def get_unsolved_challenge(language=language):
        print "Language is", language
        qs = Challenge.objects.filter(solved=False, language=language)
        if qs.exists():
            return qs.first()
        else:
            return None

    @staticmethod
    def unsolved_puzzles_left(student=True):
        max_num_puzzles = Challenge.MAX_NUM_STUDENT if student else Challenge.MAX_NUM_NON_STUDENT
        # get number of solved puzzles in a given category
        solved_puzzles = Registration.objects.filter(has_solved_challenge=True, is_student=student).count()
        return max_num_puzzles - solved_puzzles

    class Meta:
        ordering = ('-updated_at', 'solved', )

    def __unicode__(self):
        if self.pk:
            return '[{1}] {0} (#{2})'.format(self.decrypted_message, 
                'Solved' if self.solved else 'Unsolved', self.pk)
        else:
            return '[{1}] {0})'.format(self.decrypted_message, 
                'Solved' if self.solved else 'Unsolved')




