from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _


class Person(models.Model):
    class BloodType(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'

    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    blood_type = models.CharField(
        _('blood type'),
        max_length=3,
        choices=BloodType.choices,
        blank=True,
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
    )
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('person')
        verbose_name_plural = _('people')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        years = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        return years

    @property
    def initials(self):
        first = self.first_name[:1].upper() if self.first_name else ''
        last = self.last_name[:1].upper() if self.last_name else ''
        return f'{first}{last}' or '?'


class HealthEvent(models.Model):
    class EventType(models.TextChoices):
        MILESTONE = 'milestone', _('Milestone')
        ILLNESS = 'illness', _('Illness')
        INJURY = 'injury', _('Injury')
        SURGERY = 'surgery', _('Surgery')
        ALLERGY = 'allergy', _('Allergy')
        OTHER = 'other', _('Other')

    class Severity(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_('person'),
    )
    title = models.CharField(_('title'), max_length=200)
    event_type = models.CharField(
        _('event type'),
        max_length=20,
        choices=EventType.choices,
        default=EventType.OTHER,
    )
    severity = models.CharField(
        _('severity'),
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    occurred_on = models.DateField(_('occurred on'))
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['-occurred_on', '-pk']
        verbose_name = _('health event')
        verbose_name_plural = _('health events')

    def __str__(self):
        return f'{self.title} ({self.person})'


class Doctor(models.Model):
    name = models.CharField(_('name'), max_length=200)
    specialty = models.CharField(_('specialty'), max_length=200, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=50, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('doctor')
        verbose_name_plural = _('doctors')

    def __str__(self):
        return self.name


class Exam(models.Model):
    class ExamType(models.TextChoices):
        LAB = 'lab', _('Lab')
        IMAGING = 'imaging', _('Imaging')
        CHECKUP = 'checkup', _('Checkup')
        SPECIALIST = 'specialist', _('Specialist')
        REPORT = 'report', _('Report / Informe')
        OTHER = 'other', _('Other')

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name=_('person'),
    )
    event = models.ForeignKey(
        HealthEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exams',
        verbose_name=_('health event'),
        help_text=_('Optional related health event.'),
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exams',
        verbose_name=_('doctor'),
    )
    title = models.CharField(_('title'), max_length=200)
    exam_type = models.CharField(
        _('exam type'),
        max_length=20,
        choices=ExamType.choices,
        default=ExamType.OTHER,
    )
    performed_on = models.DateField(_('performed on'))
    summary = models.TextField(_('summary'), blank=True)
    provider = models.CharField(_('provider'), max_length=200, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['-performed_on', '-pk']
        verbose_name = _('exam')
        verbose_name_plural = _('exams')

    def __str__(self):
        return f'{self.title} ({self.person})'


class ExamAttachment(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('exam'),
    )
    file = models.FileField(_('file'), upload_to='exams/%Y/%m/')
    label = models.CharField(_('label'), max_length=200, blank=True)
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('exam attachment')
        verbose_name_plural = _('exam attachments')

    def __str__(self):
        return self.label or self.file.name

    @property
    def is_image(self):
        name = (self.file.name or '').lower()
        return name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'))

    @property
    def is_pdf(self):
        return (self.file.name or '').lower().endswith('.pdf')
