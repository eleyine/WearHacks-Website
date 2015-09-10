from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field, HTML, MultiField
from crispy_forms.bootstrap import FormActions, StrictButton

from registration.models import Registration, Challenge, DiscountCode
from registration.forms.helpers import PDFField

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as __
from registration.forms.helpers import (
    get_registration_button_html, 
    get_confirm_button_html,
    get_challenge_question_header,
)

class ConfirmRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = (
                'first_name',
                'last_name',
                'is_student',
                'school',
                'food_restrictions',
                'tshirt_size',
                'is_returning',
                'is_first_time_hacker',
                'has_attended',
            )

    def __init__(self, *args, **kwargs):
        super(ConfirmRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'confirmation-form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'register'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-7'


        self.helper.layout = Layout(
            HTML(get_confirm_button_html()),
            Fieldset(
                _('Staff Actions'),
                Field('has_attended', 
                    data_off_text='No', data_on_text='Yes'),
                css_class = 'staff-actions'
            ),
            Fieldset(
                _('Attendee Information'),
                'first_name',
                'last_name',
                Field('is_student', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                'school',
                Field('food_restrictions', rows=1),
                'tshirt_size',
                Field('is_returning', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                Field('is_first_time_hacker', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                css_class="attendee-info"
            ),
        )

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = (
                'first_name',
                'last_name',
                'gender',
                'is_student',
                'school',
                'email',
                'github',
                'linkedin',
                'food_restrictions',
                'tshirt_size',
                'is_returning',
                'is_first_time_hacker',
                'resume',
                'has_read_conditions',
            )

    resume = PDFField(required=False, label = _('Resume'),
        help_text=_('Not required but this might reach our sponsors for targeted employment opportunities.'))
    has_read_conditions = forms.BooleanField(required=False, 
        label = _(
            'I have read and I agree with '
            'the <a class="terms" href="#"> Terms and Conditions</a> and the '
            'the <a class="conduct" href="#"> Code of Conduct</a> '
            ))
    has_discount_code = False
    discount_code = None

    def clean(self):
        self.cleaned_data = super(RegistrationForm, self).clean()
        self.cleaned_data['solved_challenge'] = self.challenge
        self.cleaned_data['has_solved_challenge'] = False

        if 'challenge_do_attempt' in self.cleaned_data and \
            self.cleaned_data["challenge_do_attempt"]:

            # clean strings to minimise errors due to weird characters, spacing, capitalization etc.
            user_solution = self.cleaned_data["challenge_question"].lower().strip()
            user_solution = Challenge.clean_message(user_solution)
            valid_solution = self.challenge.decrypted_message.lower().strip()
            valid_solution = Challenge.clean_message(valid_solution)
            
            if user_solution == valid_solution:
                self.cleaned_data['has_solved_challenge'] = True
                # Make sure there are challenges left in this category
                if 'is_student' in self.cleaned_data:
                    spots_left = Challenge.unsolved_puzzles_left(student=self.cleaned_data["is_student"])
                    if spots_left == 0:
                        self.add_error('challenge_do_attempt', 
                            _("There are no spots left for your category. "
                              "Please uncheck this box to proceed."))
                # Avoid the same person solving challenges
                if self.cleaned_data["email"]:
                    n = Registration.objects.filter(email=self.cleaned_data["email"]).count()
                    if n > 0:
                        self.add_error('challenge_do_attempt', 
                            _("Someone who solved the puzzle already registered with your email. "
                              "Please uncheck this box to proceed."))
            else:
                self.add_error('challenge_question', _("No luck :( Try again?"))
                self.add_error('challenge_do_attempt', _("Uncheck this if you'd like to proceed without a solution."))
        
        self.data['has_solved_challenge'] = self.cleaned_data['has_solved_challenge']        
        if 'discount_code_code' in self.cleaned_data and \
            self.cleaned_data["discount_code_code"]:
            # check that discount code exists
            code = self.cleaned_data["discount_code_code"]
            self.has_discount_code = False
            self.discount_code = None
            discount_code_exists = DiscountCode.objects.filter(code=code).exists()
            if discount_code_exists:
                discount_code = DiscountCode.objects.get(code=code)
                if not discount_code.is_active:
                    self.add_error('discount_code_code', _("Sorry, this discount code is inactive."))
                elif Registration.objects.filter(discount_code=discount_code).count() >= discount_code.max_coupons:
                    self.add_error('discount_code_code', _("Sorry, we ran out of coupons for this discount code."))
                else:
                    self.has_discount_code = True
                    self.discount_code = discount_code
            else:
                self.add_error('discount_code_code', _("Sorry, this discount code doesn't exist."))

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        if 'challenge' in kwargs:
            self.challenge = kwargs.pop('challenge')
        else:
            self.challenge = None
        self.discount_code = None
        super(RegistrationForm, self).__init__(*args, **kwargs)

        # Add challenge field
        if self.challenge:
            self.fields['challenge_question'] = forms.CharField(required=False, 
                label = _('Solution'), #_('Challenge Question'),
                widget=forms.widgets.Textarea,
                help_text = _('Unlimited number of trials as long as '
                    '"submit my solution" is checked.')
                )
            self.fields['challenge_do_attempt'] = forms.BooleanField(required=False, 
                label = _('Submit my solution to the challenge question'),
                initial=True) 
            self.fields['has_solved_challenge'] = forms.BooleanField(required=False,
                widget=forms.widgets.HiddenInput,
                initial=False) 

        # Discount Code
        self.fields['discount_code_code'] = forms.CharField(required=False, 
            label = _('Discount Code'),
            )

        self.helper = FormHelper()
        self.helper.form_id = 'registration-form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'register'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-7'


        self.helper.layout = Layout(
            Fieldset(
                _('General Information'),
                'first_name',
                'last_name',
                'gender',
                'email',
            ),
            Fieldset(
                _('Tell us a bit about yourself.'),
                Div(Field('is_student', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                    css_id="is_student_wrapper"
                    ),
                Field('is_returning', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                Field('is_first_time_hacker', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                'school',
                css_id='about-you'
            ),
            Fieldset(
                _('Experience'),
                'github',
                'linkedin',
                'resume',
            ),
            Fieldset(
                _('Misc.'),
                'tshirt_size',
                Field('food_restrictions', rows=2),
            ),
        )
        if self.challenge:
            self.helper.layout.extend((
                Fieldset(
                    _('Bonus'),
                    HTML(get_challenge_question_header(self.challenge.encrypted_message)),
                    'has_solved_challenge',
                    Field('challenge_question', rows=3, placeholder=_('Easy, the answer is...')),
                    Field('challenge_do_attempt', 
                        data_off_text='No', data_on_text='Yes', data_size='mini'),
                    css_id='bonus'
                ),
            ))
        self.helper.layout.extend((
                Fieldset(
                    _('Payment Options'),
                    Field('discount_code_code', placeholder='CODE'),
                    css_id='payment'
                )
            ))
        hide_checkout_hint = self.challenge is not None
        self.helper.layout.extend((
            # Field('has_read_waiver', css_class="waiver"),
            Field('has_read_conditions', css_class="conditions"),
            HTML(get_registration_button_html(hide_checkout_hint=hide_checkout_hint)),
        ))
