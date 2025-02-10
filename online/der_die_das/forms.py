from django import forms
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Layout, Fieldset, Field, Div, Row, Column
from django.urls import reverse


from .models import Level, Lemma, Gender  # type: ignore
from .constants import LEVELS, FREQUENCIES

 
class ByLemmaForm(forms.Form):
    """Search by lemma, currently located on the main navbar"""
    search = forms.CharField(label='Search for a word'
                             , widget=forms.TextInput(
                                                attrs={ 'css_class' : "form-control",
                                                        'placeholder': "Search for a word...",
                                                        }
                                                        )
                            ) 
                

class EntryListForm(forms.Form):
    """Words list form"""
    freq_choices = [(f, f) for f in FREQUENCIES[::-1] if f is not None ] 
 
    search = forms.CharField(label='Search for a word', required=False)
    level = forms.MultipleChoiceField(choices=LEVELS,   required=False)
    frequency = forms.MultipleChoiceField(choices=freq_choices,  required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-entry-list-form'
        self.helper.form_method = 'GET'
        self.helper.form_action = ''

        field_search = Field('search', placeholder="Search for a word")
        layout =  Layout(
                        Row(  
                            Column(field_search),
                            Column('level'),
                            Column('frequency'),
                            css_class="row justify-content-auto",
                            ),
                        Submit('submit', 'Submit'),
                        Button('reset', 'Reset', css_class='btn btn-primary',
                            onclick=f"window.location='{reverse('der_die_das:entryList')}' ; return false;"),
                        )

        self.helper.layout =  layout
        self.helper.all().wrap_together(Fieldset, '', css_class="shadow p-3 mb-2 bg-warning-subtle mt-1 rounded-3")
        # check after https://django-crispy-forms.readthedocs.io/en/latest/dynamic_layouts.html#filter
   

class GameSetupForm(forms.Form):
 
    level = forms.ModelChoiceField(queryset=Level.objects.all().order_by('level'), 
                                   initial = 1,  
                                   required=True
                                   )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-game-form'
        self.helper.form_method = 'GET'
        self.helper.form_action = ''
        self.helper.layout =  Layout(
                    Div('level',
                            css_class="col"), 
                    Submit('Change', 'Change', css_class='button white'),                  
                    )
 

