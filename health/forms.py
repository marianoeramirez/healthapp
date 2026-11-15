from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Doctor, Exam, ExamAttachment, HealthEvent, Person


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = (
            'first_name',
            'last_name',
            'birth_date',
            'blood_type',
            'avatar',
            'notes',
        )
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class HealthEventForm(forms.ModelForm):
    class Meta:
        model = HealthEvent
        fields = (
            'person',
            'title',
            'event_type',
            'severity',
            'occurred_on',
            'description',
        )
        widgets = {
            'occurred_on': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = (
            'name',
            'specialty',
            'phone_number',
            'city',
            'country',
            'description',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = (
            'person',
            'event',
            'doctor',
            'title',
            'exam_type',
            'performed_on',
            'summary',
            'provider',
        )
        widgets = {
            'performed_on': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        person_id = None
        if self.data.get('person'):
            person_id = self.data.get('person')
        elif self.instance and self.instance.pk:
            person_id = self.instance.person_id
        elif self.initial.get('person'):
            person_id = self.initial.get('person')

        if person_id:
            self.fields['event'].queryset = HealthEvent.objects.filter(
                person_id=person_id
            )
        else:
            self.fields['event'].queryset = HealthEvent.objects.none()

    def clean(self):
        cleaned = super().clean()
        person = cleaned.get('person')
        event = cleaned.get('event')
        if person and event and event.person_id != person.pk:
            self.add_error(
                'event',
                _('The selected health event must belong to the same person.'),
            )
        return cleaned


ExamAttachmentFormSet = inlineformset_factory(
    Exam,
    ExamAttachment,
    fields=('file', 'label'),
    extra=3,
    can_delete=True,
)
