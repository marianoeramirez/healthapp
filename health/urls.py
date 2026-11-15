from django.urls import include, path

from . import views

people_patterns = [
    path('', views.PersonListView.as_view(), name='list'),
    path('add/', views.PersonCreateView.as_view(), name='add'),
    path('<int:pk>/', views.PersonDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PersonUpdateView.as_view(), name='edit'),
]

events_patterns = [
    path('', views.EventListView.as_view(), name='list'),
    path('add/', views.EventCreateView.as_view(), name='add'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EventUpdateView.as_view(), name='edit'),
]

doctors_patterns = [
    path('', views.DoctorListView.as_view(), name='list'),
    path('add/', views.DoctorCreateView.as_view(), name='add'),
    path('<int:pk>/', views.DoctorDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='edit'),
]

exams_patterns = [
    path('', views.ExamListView.as_view(), name='list'),
    path('upload/', views.ExamCreateView.as_view(), name='upload'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ExamUpdateView.as_view(), name='edit'),
]

urlpatterns = [
    path('', views.HomeRedirectView.as_view(), name='home'),
    path('people/', include((people_patterns, 'people'))),
    path('events/', include((events_patterns, 'events'))),
    path('doctors/', include((doctors_patterns, 'doctors'))),
    path('exams/', include((exams_patterns, 'exams'))),
]
