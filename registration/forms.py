from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Field, HTML
from crispy_forms.bootstrap import FormActions, StrictButton


from registration.models import Registration

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
                # 'tshirt_size',
                'is_returning',
                'is_hacker',
                'resume',
                'waiver'
            )

    # def clean_email(self):
        
    #     self._errors['email'] = [u'Email is already in use']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'registration-form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'register'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-6'


        self.helper.layout = Layout(
            Fieldset(
                'General Information',
                'first_name',
                'last_name',
                'gender',
                'email',
            ),
            Fieldset(
                'Tell us a bit about yourself.',
                Field('is_student', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                Field('is_returning', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                Field('is_hacker', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                'school'
            ),
            Fieldset(
                'Experience',
                'github',
                'linkedin',
                'resume',
            ),
            Fieldset(
                'Misc.',
                Field('food_restrictions', rows=2),
                'waiver',
            ),
            HTML(
                '<div class="row"><div class="col-xs-10 col-xs-offset-1 col-sm-8 col-sm-offset-2">'
                '<span id="error_id_pay" class="help-block hide"><strong>Please correct your registration information before proceeding to payment.</strong></span>'
                '<a id="id_pay" class="btn btn-large btn-block btn-success">Enter Payment Information</a>'
                '<p id="hint_id_pay" class="help-block">Payment is handled by Stripe. We do not store your card information.</p>'
                '</div></div>'
                ),
            # FormActions(
                
            #     StrictButton('Sign me up', name='register', 
            #         css_class='btn-primary pull-right page-scroll', css_id="register",
            #         href='#registration-form')
            # )
        )

