from django.contrib import admin

from .models import Doctor, Exam, ExamAttachment, HealthEvent, Person


class ExamAttachmentInline(admin.TabularInline):
    model = ExamAttachment
    extra = 1


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'blood_type')
    search_fields = ('first_name', 'last_name')
    list_filter = ('blood_type',)
    ordering = ('last_name', 'first_name')


@admin.register(HealthEvent)
class HealthEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'person', 'event_type', 'severity', 'occurred_on')
    list_filter = ('event_type', 'severity', 'person', 'occurred_on')
    search_fields = ('title', 'description', 'person__first_name', 'person__last_name')
    date_hierarchy = 'occurred_on'
    autocomplete_fields = ('person',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'phone_number', 'city', 'country')
    search_fields = (
        'name',
        'specialty',
        'phone_number',
        'city',
        'country',
        'description',
    )
    list_filter = ('specialty', 'country', 'city')
    ordering = ('name',)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'person',
        'doctor',
        'exam_type',
        'performed_on',
        'event',
        'provider',
    )
    list_filter = ('exam_type', 'person', 'doctor', 'performed_on')
    search_fields = (
        'title',
        'summary',
        'provider',
        'person__first_name',
        'person__last_name',
        'doctor__name',
    )
    date_hierarchy = 'performed_on'
    autocomplete_fields = ('person', 'event', 'doctor')
    inlines = [ExamAttachmentInline]


@admin.register(ExamAttachment)
class ExamAttachmentAdmin(admin.ModelAdmin):
    list_display = ('label', 'exam', 'uploaded_at')
    search_fields = ('label', 'exam__title')
    autocomplete_fields = ('exam',)
