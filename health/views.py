from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)

from .forms import (
    DoctorForm,
    ExamAttachmentFormSet,
    ExamForm,
    HealthEventForm,
    PersonForm,
)
from .models import Doctor, Exam, HealthEvent, Person


class HomeRedirectView(LoginRequiredMixin, RedirectView):
    pattern_name = 'people:list'


class PersonListView(LoginRequiredMixin, ListView):
    model = Person
    template_name = 'people/list.html'
    context_object_name = 'people'

    def get_queryset(self):
        return Person.objects.annotate(
            event_count=Count('events', distinct=True),
            exam_count=Count('exams', distinct=True),
        )


class PersonDetailView(LoginRequiredMixin, DetailView):
    model = Person
    template_name = 'people/detail.html'
    context_object_name = 'person'

    def get_queryset(self):
        return Person.objects.prefetch_related(
            Prefetch(
                'events',
                queryset=HealthEvent.objects.prefetch_related(
                    Prefetch(
                        'exams',
                        queryset=Exam.objects.prefetch_related('attachments'),
                    )
                ),
            ),
            Prefetch(
                'exams',
                queryset=Exam.objects.prefetch_related('attachments'),
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.object
        timeline = []

        for event in person.events.all():
            timeline.append(
                {
                    'kind': 'event',
                    'date': event.occurred_on,
                    'event': event,
                    'exams': list(event.exams.all()),
                }
            )

        standalone_exams = [exam for exam in person.exams.all() if exam.event_id is None]
        for exam in standalone_exams:
            timeline.append(
                {
                    'kind': 'exam',
                    'date': exam.performed_on,
                    'exam': exam,
                }
            )

        timeline.sort(key=lambda item: (item['date'], item['kind']), reverse=True)
        context['timeline'] = timeline
        return context


class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = 'people/form.html'

    def get_success_url(self):
        return reverse('people:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Añadir persona'
        return context


class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = 'people/form.html'

    def get_success_url(self):
        return reverse('people:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar persona'
        return context


class EventListView(LoginRequiredMixin, ListView):
    model = HealthEvent
    template_name = 'events/list.html'
    context_object_name = 'events'
    paginate_by = 50

    def get_queryset(self):
        qs = HealthEvent.objects.select_related('person').annotate(
            exam_count=Count('exams', distinct=True),
        )
        params = self.request.GET

        event_type = params.get('event_type')
        if event_type:
            qs = qs.filter(event_type=event_type)

        person_id = params.get('person')
        if person_id:
            qs = qs.filter(person_id=person_id)

        severity = params.get('severity')
        if severity:
            qs = qs.filter(severity=severity)

        date_from = params.get('from')
        if date_from:
            try:
                qs = qs.filter(occurred_on__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
            except ValueError:
                pass

        date_to = params.get('to')
        if date_to:
            try:
                qs = qs.filter(occurred_on__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
            except ValueError:
                pass

        return qs.order_by('-occurred_on', '-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['people'] = Person.objects.all()
        context['event_types'] = HealthEvent.EventType.choices
        context['severities'] = HealthEvent.Severity.choices
        context['filters'] = {
            'event_type': self.request.GET.get('event_type', ''),
            'person': self.request.GET.get('person', ''),
            'severity': self.request.GET.get('severity', ''),
            'from': self.request.GET.get('from', ''),
            'to': self.request.GET.get('to', ''),
        }
        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    model = HealthEvent
    template_name = 'events/detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return HealthEvent.objects.select_related('person').prefetch_related(
            Prefetch(
                'exams',
                queryset=Exam.objects.prefetch_related('attachments'),
            )
        )


class EventCreateView(LoginRequiredMixin, CreateView):
    model = HealthEvent
    form_class = HealthEventForm
    template_name = 'events/form.html'

    def get_initial(self):
        initial = super().get_initial()
        person_id = self.request.GET.get('person')
        if person_id:
            initial['person'] = person_id
        return initial

    def get_success_url(self):
        return reverse('events:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Añadir evento'
        return context


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = HealthEvent
    form_class = HealthEventForm
    template_name = 'events/form.html'

    def get_success_url(self):
        return reverse('events:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar evento'
        return context


class DoctorListView(LoginRequiredMixin, ListView):
    model = Doctor
    template_name = 'doctors/list.html'
    context_object_name = 'doctors'
    paginate_by = 50

    def get_queryset(self):
        qs = Doctor.objects.annotate(exam_count=Count('exams', distinct=True))
        params = self.request.GET

        q = params.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(specialty__icontains=q)
                | Q(phone_number__icontains=q)
                | Q(city__icontains=q)
                | Q(country__icontains=q)
                | Q(description__icontains=q)
            )

        specialty = params.get('specialty', '').strip()
        if specialty:
            qs = qs.filter(specialty__iexact=specialty)

        return qs.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialties'] = (
            Doctor.objects.exclude(specialty='')
            .order_by('specialty')
            .values_list('specialty', flat=True)
            .distinct()
        )
        context['filters'] = {
            'q': self.request.GET.get('q', ''),
            'specialty': self.request.GET.get('specialty', ''),
        }
        return context


class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = Doctor
    template_name = 'doctors/detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = (
            self.object.exams.select_related('person', 'event')
            .order_by('-performed_on', '-pk')
        )
        return context


class DoctorCreateView(LoginRequiredMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/form.html'

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return reverse('doctors:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Añadir médico'
        context['next'] = self.request.GET.get('next', '')
        return context


class DoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/form.html'

    def get_success_url(self):
        return reverse('doctors:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar médico'
        context['next'] = ''
        return context


class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'exams/list.html'
    context_object_name = 'exams'
    paginate_by = 50

    def get_queryset(self):
        qs = Exam.objects.select_related(
            'person', 'event', 'doctor'
        ).prefetch_related('attachments')
        params = self.request.GET

        q = params.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(summary__icontains=q)
                | Q(provider__icontains=q)
                | Q(doctor__name__icontains=q)
            )

        exam_type = params.get('exam_type')
        if exam_type:
            qs = qs.filter(exam_type=exam_type)

        person_id = params.get('person')
        if person_id:
            qs = qs.filter(person_id=person_id)

        return qs.order_by('-performed_on', '-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['people'] = Person.objects.all()
        context['exam_types'] = Exam.ExamType.choices
        context['filters'] = {
            'q': self.request.GET.get('q', ''),
            'exam_type': self.request.GET.get('exam_type', ''),
            'person': self.request.GET.get('person', ''),
        }
        return context


class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = 'exams/detail.html'
    context_object_name = 'exam'

    def get_queryset(self):
        return Exam.objects.select_related(
            'person', 'event', 'doctor'
        ).prefetch_related('attachments')



class ExamFormsetMixin:
    def get_events_by_person(self):
        return {
            str(person.pk): [
                {'id': event.pk, 'title': event.title}
                for event in person.events.all()
            ]
            for person in Person.objects.prefetch_related('events')
        }

    def get_formset(self, instance=None):
        if instance is None:
            instance = getattr(self, 'object', None)
        if self.request.method == 'POST':
            return ExamAttachmentFormSet(
                self.request.POST,
                self.request.FILES,
                instance=instance,
            )
        return ExamAttachmentFormSet(instance=instance)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = kwargs.get('formset') or self.get_formset()
        context['events_by_person'] = self.get_events_by_person()
        return context

    def post(self, request, *args, **kwargs):
        if isinstance(self, UpdateView):
            self.object = self.get_object()
        else:
            self.object = None
        form = self.get_form()
        formset = self.get_formset(instance=self.object)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


class ExamCreateView(LoginRequiredMixin, ExamFormsetMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'exams/form.html'

    def get_initial(self):
        initial = super().get_initial()
        person_id = self.request.GET.get('person')
        event_id = self.request.GET.get('event')
        if person_id:
            initial['person'] = person_id
        if event_id:
            initial['event'] = event_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Subir examen'
        return context

    def get_success_url(self):
        return reverse('exams:detail', kwargs={'pk': self.object.pk})


class ExamUpdateView(LoginRequiredMixin, ExamFormsetMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'exams/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar examen'
        return context

    def get_success_url(self):
        return reverse('exams:detail', kwargs={'pk': self.object.pk})
