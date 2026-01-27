from django import forms
from django.utils import timezone
from index.models import Attendance, LeaveApplication, StaffReg

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['first_hour', 'second_hour', 'third_hour', 'fourth_hour', 'fifth_hour']
        widgets = {
            field: forms.Select(choices=Attendance.CHOICE, attrs={'class': 'form-select'})
            for field in fields
        }


class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['reason', 'leave_type', 'start_date', 'end_date']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please provide a reason for your leave.'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # The view passes a 'user' argument. We pop it from kwargs before
        # passing them to the parent class's __init__ to avoid a TypeError,
        # as the base ModelForm does not expect a 'user' argument.
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be before start date.")
            
            # Ensure dates are not in the past (except for today)
            today = timezone.now().date()
            if start_date < today:
                raise forms.ValidationError("Cannot apply for leave with a start date in the past.")
            if end_date < today:
                raise forms.ValidationError("Cannot apply for leave with an end date in the past.")
        
        return cleaned_data