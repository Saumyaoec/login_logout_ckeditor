from django import forms


class ContactForm(forms.Form):

    from_email = forms.EmailField(required=True)
    from_name = forms.CharField(required=True)
    phone = forms.IntegerField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
