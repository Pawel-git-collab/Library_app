import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import BookInstance
from django.contrib.auth.models import User


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Wprowadz date w zakresie od dzis do 4 tygodni (domyslnie 3 tygodnie od dziś).", required=True)

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        if data < datetime.date.today():
            raise ValidationError(_('Niepoprawna data - data sprzed dnia dzisiejszego.'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Niepoprawna data - wykracza poza dozwolone 4 tygodnie liczone od dziś.'))

        return data


class ConfirmGetBook(forms.Form):
    def clean_get_book(self):
        status = self.cleaned_data['status']
        return status

    LOAN_STATUS = (
        ('m', 'W trakcie renowacji'),  # m - maintenance
        ('a', 'Dostępna'),  # a - available
    )

    status = forms.ChoiceField(choices=LOAN_STATUS)


class ReversationBookForm(forms.Form):
    def clean_reserwation_book(self):
        status = self.cleaned_data['status']
        return status

    LOAN_STATUS = (
        ('r', 'Zarezerwowana'),  # r - reserved
        ('o', 'Wypożyczona'),  # o - on loan
    )

    status = forms.ChoiceField(choices=LOAN_STATUS)


class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ('status', 'borrower')

    def __init__(self, *args, **kwargs):
        super(BookInstanceForm, self).__init__(*args, **kwargs)
        self.fields['borrower'].queryset = User.objects.filter(username=kwargs['initial']['borrower'])
        self.fields['borrower'].empty_label = None

    # def get_initial(self):
    #     self.borrower = User.username.objects.get(pk=self.kwargs.get('pk'))
    #     return {'borrower': self.borrower}
    #
    # def borrower_book(self):
    #     borrower = self.cleaned_data['borrower']
    #     return borrower
    #
    # borrower = forms.ChoiceField(choices=User.username.objects.get(pk=self.kwargs.get('pk'))

    def clean_reservation_book(self):
        status = self.cleaned_data['status']
        return status

    LOAN_STATUS = (
        ('o', 'Wypożyczona'),
        ('r', 'Zarezerwowana'),
    )

    status = forms.ChoiceField(choices=LOAN_STATUS)

    wypożyczona_do = forms.DateField(
        help_text="Wprowadz date w zakresie od dzis do 4 tygodni (domyslnie 3 tygodnie od dziś).", required=True)

    def clean_renewal_date(self):
        data = self.cleaned_data['wypożyczona_do']

        if data < datetime.date.today():
            raise ValidationError(_('Niepoprawna data - data sprzed dnia dzisiejszego.'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Niepoprawna data - wykracza poza dozwolone 4 tygodnie liczone od dziś.'))

        return data
