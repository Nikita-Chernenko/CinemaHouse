from django import forms


class ReservationForm(forms.Form):
    name = forms.CharField(max_length=20)
    surname = forms.CharField(max_length=20)
    email = forms.EmailField()


