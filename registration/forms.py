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
                Div(Field('is_student', 
                    data_off_text='No', data_on_text='Yes', data_size='mini'),
                    css_id="is_student_wrapper"
                    ),
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
                '<div class="row"><div class="col-xs-12 col-sm-6 col-sm-offset-3 text-center checkout-wrapper">'
                '<span id="registration-error" class="help-block hide message message-error"><strong>Registration Failure Message</strong></span>'
                '<a id="register" class="registration-form-action register-action mobile btn btn-lg btn-block btn-primary"><i class="fa fa-lock hide"></i><i class="fa fa-paper-plane"></i><i class="fa fa-spinner fa-pulse hide"></i><i class="fa fa-check hide"></i> <span class="text">Register</span></a>'
                '<span id="server-error" class="help-block hide message message-error"><strong>Temporary problem with our server</strong></span>'
                '<span id="checkout-error" class="help-block hide message message-error"><strong>Checkout Failure Message</strong></span>'
                '<span id="success-message" class="help-block hide message message-success"><strong>Things are going great yo.</strong></span>'
                '<a id="checkout" class="registration-form-action checkout-action mobile disabled btn btn-lg btn-block btn-primary"><i class="fa fa-lock"></i><i class="fa fa-unlock hide"></i><i class="fa fa-paper-plane hide"></i><i class="fa fa-spinner fa-pulse hide"></i><i class="fa fa-check hide"></i> <span class="text">Checkout</span></a>'
                '<a id="checkout" class="registration-form-action checkout-action register-action desktop btn btn-lg btn-block btn-primary"><i class="fa fa-lock"></i><i class="fa fa-paper-plane hide"></i><i class="fa fa-spinner fa-pulse hide"></i><i class="fa fa-check hide"></i> <span class="text">Checkout</span></a>'
                '<p id="hint_checkout" class="has-info help-block">Payment is handled by Stripe. We do not store your card information.</p>'
                '</div></div>'
                ),
            # FormActions(
                
            #     StrictButton('Sign me up', name='register', 
            #         css_class='btn-primary pull-right page-scroll', css_id="register",
            #         href='#registration-form')
            # )
        )

