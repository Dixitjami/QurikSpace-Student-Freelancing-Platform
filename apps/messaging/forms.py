from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Type your message...',
                'class': 'w-full rounded-full border border-ink/10 bg-white px-5 py-3 text-sm font-medium text-ink placeholder:text-ink/35 focus:outline-none focus:ring-2 focus:ring-coral/25',
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'hidden',
                'id': 'id_message_file',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        content = (cleaned_data.get('content') or '').strip()
        file = cleaned_data.get('file')

        # Allow text, file, or both; block empty submissions.
        if not content and not file:
            raise forms.ValidationError("Add a message or attach a file before sending.")

        cleaned_data['content'] = content
        return cleaned_data
