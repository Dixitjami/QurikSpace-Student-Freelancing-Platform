from django import forms

from .models import RecommendationRequest


class RecommendationRequestForm(forms.ModelForm):
    class Meta:
        model = RecommendationRequest
        fields = [
            'project_title',
            'project_description',
            'required_skills',
            'budget',
            'delivery_deadline',
        ]
        widgets = {
            'project_title': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500',
                'placeholder': 'Example: Ecommerce website redesign',
            }),
            'project_description': forms.Textarea(attrs={
                'class': 'w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500',
                'rows': 5,
                'placeholder': 'Describe the project goals, features, and expected deliverables.',
            }),
            'required_skills': forms.TextInput(attrs={
                'class': 'w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500',
                'placeholder': 'Example: Django, UI design, payment gateway',
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500',
                'min': '1',
                'step': '0.01',
            }),
            'delivery_deadline': forms.NumberInput(attrs={
                'class': 'w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500',
                'min': '1',
            }),
        }

