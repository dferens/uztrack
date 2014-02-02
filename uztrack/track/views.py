from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from django_tables2 import SingleTableView

from .models import Way, TrackedWay
from .forms import WayCreateForm, TrackedWayCreateForm, \
                   WayDetailForm, TrackedWayDetailForm
from .tables import WayTable, TrackedWayTable


class WayCreateView(CreateView):
    form_class = WayCreateForm
    template_name = 'track/way_create.html'

    def get_success_url(self):
        return reverse('way_list')


class TrackedWayCreateView(CreateView):
    form_class = TrackedWayCreateForm
    template_name = 'track/trackedway_create.html'

    def get_success_url(self):
        return reverse('track_list')


class WayDetailView(UpdateView):
    model = Way
    form_class = WayDetailForm


class TrackedWayEditView(UpdateView):
    model = TrackedWay
    form_class = TrackedWayDetailForm


class TrackedWayDetailView(DetailView):
    model = TrackedWay
    template_name = 'track/trackedway_detail.html'
    context_object_name = 'tracked_way'

    def get_context_data(self, **kwargs):
        context = super(TrackedWayDetailView, self).get_context_data(**kwargs)
        return context


class WayListView(SingleTableView):
    model = Way
    table_class = WayTable


class TrackedWayListView(SingleTableView):
    model = TrackedWay
    table_class = TrackedWayTable