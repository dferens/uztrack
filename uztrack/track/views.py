import json

from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone

from django_tables2 import SingleTableView
from braces.views import LoginRequiredMixin, AjaxResponseMixin, JSONResponseMixin

from core.utils import JsonResponse
from . import forms, models, tables
from .tables import WayTable, TrackedWayTable


class Home(TemplateView):
    template_name = 'home.html'


class TrackedWayCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.TrackedWayCreateForm
    success_url = reverse_lazy('trackedway-list')
    template_name = 'track/trackedway_create.html'

    def form_valid(self, form):
        self.object = form.save(self.request)
        return JsonResponse({'redirect': self.get_success_url()})

    def form_invalid(self, form):
        return JsonResponse({'errors': form.errors})


class TrackedWayEditView(LoginRequiredMixin, UpdateView):
    model = models.TrackedWay
    form_class = forms.TrackedWayDetailForm


class TrackedWayDetailView(LoginRequiredMixin, DetailView):
    queryset = models.TrackedWay.objects.select_related('way')
    template_name = 'track/trackedway_detail.html'
    context_object_name = 'tracked_way'


class TrackedWayListView(LoginRequiredMixin, TemplateView):

    template_name = 'track/trackedway_list.html'

    def get_context_data(self, **kwargs):
        context = super(TrackedWayListView, self).get_context_data(**kwargs)

        tracked_ways = models.TrackedWay.objects.select_related('way')
        tables_data = {
            'repeated': filter(lambda way: way.is_repeated, tracked_ways),
            'nonrepeated': filter(lambda way: not way.is_repeated, tracked_ways)
        }
        for name in tables_data:
            table = tables.TrackedWayTable(tables_data[name])
            context['table_%s' % name] = table

        return context


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


