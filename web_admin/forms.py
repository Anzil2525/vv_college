from django import forms
from index.models import Course, MinorCourse, UpiPaymentSettings
from index.models import Positions, StaffReg

class Course_form(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course']


class MinorCourse_form(forms.ModelForm):
    class Meta:
        model = MinorCourse
        fields = ['course']


class Positions_form(forms.ModelForm):
    class Meta:
        model = Positions
        fields = ['pos']

class StaffPromotion(forms.ModelForm):
    class Meta:
        model = StaffReg
        fields = ['pos']


class UpiPaymentSettingsForm(forms.ModelForm):
    class Meta:
        model = UpiPaymentSettings
        fields = ['upi_id', 'upi_phone', 'qr_code', 'is_active']