from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field, HTML, MultiField
from crispy_forms.bootstrap import FormActions, StrictButton

from registration.models import Registration
from registration.forms.helpers import PDFField

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as __
from registration.forms.helpers import get_registration_button_html, get_confirm_button_html

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
                'has_attended',
                css_class = 'staff-actions'
            ),
            Fieldset(
                _('Attendee Information'),
                'first_name',
                'last_name',
                'is_student',
                'school',
                Field('food_restrictions', rows=1),
                'tshirt_size',
                'is_returning',
                'is_first_time_hacker',
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
                'has_read_waiver',
                'has_read_code_of_conduct',
            )

    resume = PDFField(required=False, label = _('Resume'),
        help_text=_('Not required but this might reach our sponsors for targeted employment opportunities.'))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
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
            Field('has_read_waiver', css_class="waiver"),
            Field('has_read_code_of_conduct', css_class="conduct"),
            HTML(get_registration_button_html())
        )
