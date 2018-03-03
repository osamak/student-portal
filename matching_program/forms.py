from django import forms
from django.contrib.auth.models import User

from accounts.models import CommonProfile
from matching_program import utils
from models import ResearchProject, StudentApplication



class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = ['title','supervisor','description','field',
                  'required_role','communication', 'status']

    def __init__(self,user, *args, **kwargs):
        from django.forms.widgets import HiddenInput
        super(ResearchProjectForm, self).__init__(*args, **kwargs)
        if user.user.is_superuser or utils.is_matchingProgram_coordinator_or_member(user.user) == False:
            self.fields['status'].widget = HiddenInput()
        

     
 

class StudentApplicationForm(forms.ModelForm):
    class Meta:
        model = StudentApplication
        fields = ['skills','experience', 'advantages']


