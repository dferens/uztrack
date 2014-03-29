from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from django_tables2 import SingleTableView
from braces.views import LoginRequiredMixin

from .models import Way, TrackedWay
from track.forms import WayCreateForm, TrackedWayCreateForm, \
                        WayDetailForm, TrackedWayDetailForm
from .tables import WayTable, TrackedWayTable


class WayCreateView(LoginRequiredMixin, CreateView):
    form_class = WayCreateForm
    template_name = 'track/way_create.html'

    def get_success_url(self):
        return reverse('way-list')


class TrackedWayCreateView(LoginRequiredMixin, CreateView):
    form_class = TrackedWayCreateForm
    template_name = 'track/trackedway_create.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('trackedway-list')


class WayDetailView(LoginRequiredMixin, UpdateView):
    model = Way
    form_class = WayDetailForm


class TrackedWayEditView(LoginRequiredMixin, UpdateView):
    model = TrackedWay
    form_class = TrackedWayDetailForm


class TrackedWayDetailView(LoginRequiredMixin, DetailView):
    model = TrackedWay
    template_name = 'track/trackedway_detail.html'
    context_object_name = 'tracked_way'


class WayListView(LoginRequiredMixin, SingleTableView):
    model = Way
    table_class = WayTable


class TrackedWayListView(LoginRequiredMixin, SingleTableView):
    model = TrackedWay
    table_class = TrackedWayTable
