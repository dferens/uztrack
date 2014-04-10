import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone

from django_tables2 import SingleTableView
from braces.views import LoginRequiredMixin, AjaxResponseMixin, JSONResponseMixin

from . import forms, models
from .tables import WayTable, TrackedWayTable


class WayCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.WayCreateForm
    template_name = 'track/way_create.html'

    def get_success_url(self):
        return reverse('way-list')


class WayDetailView(LoginRequiredMixin, UpdateView):
    context_object_name = 'way'
    form_class = forms.WayDetailForm
    model = models.Way


class WayListView(LoginRequiredMixin, SingleTableView):
    model = models.Way
    table_class = WayTable

class TrackedWayCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.TrackedWayCreateForm
    template_name = 'track/trackedway_create.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('trackedway-list')


class TrackedWayEditView(LoginRequiredMixin, UpdateView):
    model = models.TrackedWay
    form_class = forms.TrackedWayDetailForm


class TrackedWayDetailView(LoginRequiredMixin, DetailView):
    model = models.TrackedWay
    template_name = 'track/trackedway_detail.html'
    context_object_name = 'tracked_way'


class TrackedWayListView(LoginRequiredMixin, SingleTableView):
    model = models.TrackedWay
    table_class = TrackedWayTable


class HistoryRelatedMixin(object):

    def get_object(self, queryset=None):
        date_format = models.TrackedWayDayHistory.ABSOLUTE_URL_DATE_FORMAT
        dt = timezone.datetime.strptime(self.kwargs['date'], date_format)
        return get_object_or_404(models.TrackedWayDayHistory,
                                 tracked_way_id=self.kwargs['pk'],
                                 departure_date=dt.date())


class TrackedWayHistoryDetailView(LoginRequiredMixin, HistoryRelatedMixin,
                                  DetailView):
    context_object_name = 'history'    
    model = models.TrackedWayDayHistory
    template_name = 'track/trackedway_history_detail.html'


class SubscriptionMixin(HistoryRelatedMixin):
    context_object_name = 'subscription'
    model = models.HistorySubscription
    form_class = forms.HistorySubscriptionForm

    def get_object(self, queryset=None):
        history = super(SubscriptionMixin, self).get_object(queryset)
        return history.subscription


class HistorySubscriptionDetailView(LoginRequiredMixin, SubscriptionMixin,
                                    AjaxResponseMixin,
                                    DetailView):
    template_name = 'track/history_subscription_detail.html'

    def post_ajax(self, request, **kwargs):
        form = forms.HistorySubscriptionForm(request.POST,
                                             instance=self.get_object())
        if form.is_valid():
            form.save()
            context = {'success': False}
        else:
            context = {'success': True, 'errors': form._errors}

        return HttpResponse(json.dumps(context))


