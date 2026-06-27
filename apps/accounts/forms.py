from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import ClientProfile, CustomUser, Portfolio, StudentProfile



class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password1', 'password2']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['title', 'description', 'project_link', 'image']



class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = StudentProfile
        fields = [
            'bio',
            'skills',
            'experience_level',
            'is_available',
            'university',
            'degree',
            'field_of_study',
            'graduation_year',
            'resume',
            'student_id_card',
            'enrollment_proof',
        ]

        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
                'rows': 4,
            }),

            'skills': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),

            'experience_level': forms.Select(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),

            'university': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),

            'degree': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),

            'field_of_study': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),

            'graduation_year': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),

            'resume': forms.ClearableFileInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),
            'student_id_card': forms.ClearableFileInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),
            'enrollment_proof': forms.ClearableFileInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
            }),
        }

    def _validate_supporting_document(self, uploaded_file, field_name):
        if not uploaded_file:
            return uploaded_file

        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        extension = uploaded_file.name.rsplit('.', 1)[-1].lower() if '.' in uploaded_file.name else ''

        if extension not in allowed_extensions:
            raise forms.ValidationError(
                f"{field_name} must be one of: PDF, JPG, JPEG, PNG."
            )
        return uploaded_file

    def clean_student_id_card(self):
        return self._validate_supporting_document(
            self.cleaned_data.get('student_id_card'),
            'ID document'
        )

    def clean_enrollment_proof(self):
        return self._validate_supporting_document(
            self.cleaned_data.get('enrollment_proof'),
            'Supporting proof'
        )


class ClientProfileEditForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ['company_name', 'business_type']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
                'placeholder': 'Enter business/company name',
            }),
            'business_type': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-lg p-3 focus:ring-2 focus:ring-teal-500 focus:outline-none',
                'placeholder': 'Enter business type (e.g. IT Services, E-commerce)',
            }),
        }
