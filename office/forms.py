from django import forms
from decimal import Decimal
from django.utils import timezone
from index.models import Course, DepTable, FeePayment, FeeStructure, StudentFee
from .models import OfficeLeaveApplication


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['semester', 'amount', 'due_date']
        widgets = {
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ['total_amount', 'due_date']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class FeePaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.remaining_amount = kwargs.pop('remaining_amount', None)
        super().__init__(*args, **kwargs)
        if self.remaining_amount is not None:
            self.fields['amount'].widget.attrs['max'] = self.remaining_amount

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= Decimal('0'):
            raise forms.ValidationError('Payment amount must be greater than zero.')
        if self.remaining_amount is not None and amount > self.remaining_amount:
            raise forms.ValidationError(
                f'Payment cannot exceed the remaining balance of {self.remaining_amount}.'
            )
        return amount

    class Meta:
        model = FeePayment
        fields = ['amount', 'payment_date', 'payment_method', 'reference_number', 'remarks']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cash, UPI, Bank transfer'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional'}),
        }


class StudentPaymentSearchForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Student name',
    }))
    semester = forms.IntegerField(required=False, min_value=1, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Semester',
    }))
    year_of_admision = forms.IntegerField(required=False, min_value=1900, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Admission year',
    }))
    course = forms.ModelChoiceField(required=False, queryset=Course.objects.order_by('course'), widget=forms.Select(attrs={
        'class': 'form-select',
    }))
    department = forms.ModelChoiceField(required=False, queryset=DepTable.objects.order_by('dep'), widget=forms.Select(attrs={
        'class': 'form-select',
    }))
    reg_no = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Registration number',
    }))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Phone number',
    }))

    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_id', None)
        super().__init__(*args, **kwargs)
        if department_id:
            self.fields['course'].queryset = Course.objects.filter(
                dep_id=department_id
            ).order_by('course')

        course_id = self.data.get('course') if self.is_bound else None
        if course_id and not department_id:
            try:
                self.initial['department'] = Course.objects.values_list(
                    'dep_id', flat=True
                ).get(id=course_id)
            except Course.DoesNotExist:
                pass

class OfficeLeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = OfficeLeaveApplication
        fields = ['reason', 'leave_type', 'start_date', 'end_date', 'day_type']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please describe the reason for your leave.'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be before start date.")
            
            today = timezone.now().date()
            if start_date < today:
                raise forms.ValidationError("Cannot apply for leave with a start date in the past.")
        
        return cleaned_data
