from django import forms
from .models import *
from django.forms import inlineformset_factory


class DepTableForm(forms.ModelForm):
    class Meta:
        model = DepTable
        fields = "__all__"


class LoginTableForm(forms.ModelForm):
    class Meta:
        model = LoginTable
        exclude = ['status', 'user', 'rejection_reason']


class LoginEditForm(forms.ModelForm):
    class Meta:
        model = LoginTable
        fields = ['email']


class StaffRegForm(forms.ModelForm):
    class Meta:
        model = StaffReg
        exclude = ['login_info']


class StaffEditReg(forms.ModelForm):
    class Meta:
        model = StaffReg
        exclude = ['login_info', 'pos']
        

class GuadinRegForm(forms.ModelForm):
    class Meta:
        model = GuadinReg
        fields  = '__all__'


class StudentRegForm(forms.ModelForm):
    class Meta:
        model = StudentReg
        exclude = ['login_info', 'parent_1']
        labels = {
            'reg_no': 'Reg No / APAAR ID'
        }
        
    
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

class GuardianVerificationRegistration(forms.Form):
    name = forms.CharField()
    phone = forms.CharField(max_length=10)
    email = forms.EmailField()
    password = forms.CharField(max_length=20)


class TimeTableForm(forms.ModelForm): 
    class Meta: 
        model = TimeTable 
        fields = [ 
            'sem', 'day', 'first_hour_subject', 'first_houre_staff', 
            'second_hour_subject', 'second_hour_staff', 'third_hour_subject', 
            'third_hour_staff', 'fourth_hour_subject', 'fourth_hour_staff', 
            'fifth_hour_subject', 'fifth_hour_staff'

        ] 
        widgets = { 
            'course': forms.Select(
                attrs={'class': 'form-select'}), 
            'day': forms.Select(
                attrs={'class': 'form-select'}), 
            'sem': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 1, 'max': 8}), 
            'first_hour_subject': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'first_houre_staff': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'second_hour_subject': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'second_hour_staff': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'third_hour_subject': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'third_hour_staff': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'fourth_hour_subject': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'fourth_hour_staff': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'fifth_hour_subject': forms.TextInput(
                attrs={'class': 'form-control'}), 
            'fifth_hour_staff': forms.TextInput(
                attrs={'class': 'form-control'})
            }


class ExamRegistrationForm(forms.ModelForm):
    class Meta:
        model = ExamRegistration
        fields = ['exam_type', 'exam_date', 'subject', 'total_mark']
        widgets = {
            'exam_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'total_mark': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
        
class MarkListForm(forms.ModelForm):
    class Meta:
        model = MarkList
        fields = ['student', 'marks']
        
MarkListFormSet = inlineformset_factory(
    ExamRegistration,
    MarkList,
    fields=('student', 'marks'),
    extra=1,
    can_delete=False
)
