from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from .models import Way
from .forms import WayCreateForm


class WayCreateView(CreateView):
    model = Way
    form_class = WayCreateForm
    template_name = 'track/way_create.html'

    def get_success_url(self):
        return reverse('way_list')


class WayListView(ListView):
    model = Way
