import operator
from dateutil import rrule
from datetime import time

from django.db import models
from django.dispatch import Signal
from django.conf import settings
from django.contrib import admin, sites
from django.core import mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.functional import cached_property

from bitfield import BitField
from jsonfield import JSONField
from annoying.fields import AutoOneToOneField

from core.uzgovua import data
from core.utils import total_seconds
from . import utils


class Way(models.Model):
    """
    Defines abstract directed way between two train stations.
    """
    class Meta:
        unique_together = (('station_id_from', 'station_id_to'),)

    station_id_from = models.IntegerField()
    station_from = models.CharField(max_length=30)
    station_id_to = models.IntegerField()
    station_to = models.CharField(max_length=30)

    def __unicode__(self):
        return u'%s - %s' % (self.station_from, self.station_to)


class TrackedWay(models.Model):
    """
    Says that particular way should be checked for tickets on given departure weekdays.
    """
    way = models.ForeignKey(Way)
    days = BitField(flags=utils.WEEKDAYS.keys())
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    departure_date = models.DateField(null=True, blank=True)
    dep_min_time = models.TimeField(null=True, blank=True, verbose_name=u'departure min time')
    dep_max_time = models.TimeField(null=True, blank=True, verbose_name=u'departure max time')
    arr_min_time = models.TimeField(null=True, blank=True, verbose_name=u'arrival min time')
    arr_max_time = models.TimeField(null=True, blank=True, verbose_name=u'arrival max time')

    def __unicode__(self):
        return self.way.__unicode__()

    @property
    def is_repeated(self):
        return self.departure_date is None

    @property
    def active_histories(self):
        """
        Returns collection of closest :class:`History` objects for a given way.
        Creates new records if needed.
        """
        from .models import TrackedWayDayHistory as History
        from .queries import get_search_till_date

        closest_dates = self.next_dates(get_search_till_date())

        if self.is_repeated:
            found_histories = History.objects.filter(active=True,
                                                     departure_date__in=closest_dates)
            found_dates = found_histories.values_list('departure_date', flat=True)
            not_found_dates = filter(lambda d: d not in found_dates, closest_dates)
            histories_list = list(found_histories)
            histories_list.extend(self.histories.create(departure_date=date)
                                  for date in not_found_dates)
            return histories_list
        else:
            histories = self.histories.all()[:1]
            return [] if histories[0].active is False else histories

    def get_absolute_url(self):
        return reverse('trackedway-detail', kwargs=dict(pk=self.pk))

    def get_edit_url(self):
        return reverse('trackedway-edit', kwargs=dict(pk=self.pk))

    def get_delete_url(self):
        return '#'

    def next_dates(self, till):
        """
        Returns list of next arrival dates, starting from now.

        :param till: :class:`datetime.date` object, specified upper limit
        :return: list of :class:`datetime.date` objects
        """
        starts_from = timezone.now()

        if self.is_repeated:
            dateutil_weekdays = map(utils.get_dateutil_weekday, self.selected_weekdays)
            rule = rrule.rrule(rrule.WEEKLY, byweekday=dateutil_weekdays, until=till)
            return [x.date() for x in rule]
        else:
            is_expired = starts_from.date() > self.departure_date
            return [] if is_expired else [self.departure_date]

    @property
    def selected_weekdays(self):
        """
        Returns days it should check tickets on.
        Makes sense for repeated t-ways only.

        :return: generator of weekday names, like ('Monday', 'Friday', ...)
        """
        return (wday for wday, is_set in self.days if is_set)

    def save(self, is_critical=None):
        created = self.pk is None
        super(TrackedWay, self).save()

        if not self.is_repeated:
            kwargs = dict(departure_date=self.departure_date)
            kwargs.update(is_critical=True) if is_critical else None
            self.histories.create(**kwargs)

        if created and settings.POLLER_AUTOSTART_NEW:
            import poller.tasks
            poller.tasks.startup_tracked_way.delay(self.id)


class TrackedWayDayHistory(models.Model):
    """
    Describes tickets history for a given :class:`TrackedWay` way for a given day

    Field ``places_appeared`` points to :class:`TrackedWayDayHistorySnapshot`
    snapshot, when tickets were been found for the first time.
    Field ``places_disappeared`` points to :class:`TrackedWayDayHistorySnapshot`
    snapshot, when tickets were not been found for the first time.
    """
    class Meta:
        ordering = ['departure_date']
        verbose_name = u'tracked way history'
        verbose_name_plural = u'tracked way histories'
        unique_together = (('tracked_way', 'departure_date'))
    
    ABSOLUTE_URL_DATE_FORMAT = '%Y-%m-%d'

    active = models.BooleanField(default=True)
    tracked_way = models.ForeignKey(TrackedWay, related_name='histories')
    departure_date = models.DateField()
    is_critical = models.BooleanField(default=False)
    places_appeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                            related_name='marks_appear', null=True)
    places_disappeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                               related_name='marks_disappear', null=True)

    on_places_appeared = Signal()
    on_places_disappeared = Signal()

    def __unicode__(self):
        return u'%s on %s' % (self.tracked_way, self.departure_date)

    def get_url_kwargs(self):
        date = self.departure_date.strftime(self.ABSOLUTE_URL_DATE_FORMAT)
        return dict(pk=self.tracked_way_id, date=date)

    def get_absolute_url(self):
        return reverse('trackedway-history-detail',
                        kwargs=self.get_url_kwargs())

    def get_subscription_url(self):
        return reverse('history-subscription-detail',
                        kwargs=self.get_url_kwargs())

    @property
    def relevance(self):
        elapsed = timezone.now() - self.last_snapshot.made_on
        elapsed_percentage = (total_seconds(elapsed) * 100 /
                              total_seconds(settings.POLLER_INTERVAL))
        return (elapsed, elapsed_percentage)

    @cached_property
    def last_snapshot(self):
        return self.snapshots.latest()

    @property
    def has_seats(self):
        return self.last_snapshot.total_places_count > 0

    @property
    def days_left(self):
        today =  timezone.datetime.today().date()
        return (self.departure_date - today).days

    def check_snapshot(self, snapshot):
        """
        Checks that places for current way history were appeared or disappeared
        within given snapshot.
        """
        if self.places_appeared is None:
            if snapshot.total_places_count > 0:
                self.subscription.notify_places_appeared(snapshot)
                self.places_appeared = snapshot
                self.save()
                self.on_places_appeared.send(sender=self)
        elif self.places_disappeared is None:
            if snapshot.total_places_count == 0:
                self.subscription.notify_places_disappeared(snapshot)
                self.places_disappeared = snapshot
                self.save()
                self.on_places_disappeared.send(sender=self)
        else:
            # Regular snapshot
            pass


class HistorySubscription(models.Model):
    class Meta:
        verbose_name = u'history subscription'

    DEFAULT_SUBJECT = 'Subscription update'
    CRITICAL_PREFIX = '[CRITICAL]'
    DEFAULT_TEMPLATE = 'email/subscription'

    enabled = models.BooleanField(default=False)
    history = AutoOneToOneField(TrackedWayDayHistory, related_name='subscription')

    @property
    def target_user(self):
        return self.history.tracked_way.owner

    def get_absolute_url(self):
        return self.history.get_subscription_url()

    def _notify(self, context, subject=None, template=None):
        if self.enabled:
            prefix = settings.EMAIL_SUBJECT_PREFIX
            prefix += self.CRITICAL_PREFIX if self.history.is_critical else ''
            subject = '%s %s' % (prefix, subject or self.DEFAULT_SUBJECT)
            from_email = settings.EMAIL_HOST_USER
            to_email = self.target_user.email
            context.update(subscription=self, history=self.history,
                           tracked_way=self.history.tracked_way,
                           SITE=sites.models.Site.objects.get_current().domain)
            template = template or self.DEFAULT_TEMPLATE
            text_content = render_to_string(template + '.txt', context)
            html_content = render_to_string(template + '.html', context)

            message = mail.EmailMultiAlternatives(subject, text_content,
                                                  from_email, [to_email])
            message.attach_alternative(html_content, 'text/html')
            message.send()

    def notify_places_appeared(self, snapshot):
        context = {    
            'title': '%d new tickets appeared' % snapshot.total_places_count,            
        }
        self._notify(context, template='email/places_appeared')

    def notify_places_disappeared(self, snapshot):
        self._notify({
            'title': 'Tickets for your subscription just have run out',
        })


class TrackedWayDayHistorySnapshot(models.Model):
    """
    Tickets history snapshot.
    """
    class Meta:        
        verbose_name = u'history snapshot'
        verbose_name_plural = u'history snapshots'
        get_latest_by = 'made_on'

    history = models.ForeignKey(TrackedWayDayHistory, related_name='snapshots')
    made_on = models.DateTimeField(auto_now_add=True)
    total_places_count = models.IntegerField()
    snapshot_data = JSONField()

    @property
    def route_trains(self):
        return data.RouteTrains(self.snapshot_data)

    def save(self, *args, **kwargs):
        super(TrackedWayDayHistorySnapshot, self).save(*args, **kwargs)
        self.history.check_snapshot(self)
