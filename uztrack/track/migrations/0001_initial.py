# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Way'
        db.create_table(u'track_way', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station_id_from', self.gf('django.db.models.fields.IntegerField')()),
            ('station_from', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('station_id_to', self.gf('django.db.models.fields.IntegerField')()),
            ('station_to', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'track', ['Way'])

        # Adding unique constraint on 'Way', fields ['station_id_from', 'station_id_to']
        db.create_unique(u'track_way', ['station_id_from', 'station_id_to'])

        # Adding model 'TrackedWay'
        db.create_table(u'track_trackedway', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('way', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['track.Way'])),
            ('days', self.gf('django.db.models.fields.BigIntegerField')(default=None)),
            ('start_time', self.gf('django.db.models.fields.TimeField')(default=datetime.time(0, 0))),
        ))
        db.send_create_signal(u'track', ['TrackedWay'])

        # Adding model 'TrackedWayDayHistory'
        db.create_table(u'track_trackedwaydayhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tracked_way', self.gf('django.db.models.fields.related.ForeignKey')(related_name='histories', to=orm['track.TrackedWay'])),
            ('departure_date', self.gf('django.db.models.fields.DateField')()),
            ('places_appeared', self.gf('django.db.models.fields.related.OneToOneField')(related_name='marks_appear', unique=True, null=True, to=orm['track.TrackedWayDayHistorySnapshot'])),
            ('places_disappeared', self.gf('django.db.models.fields.related.OneToOneField')(related_name='marks_disappear', unique=True, null=True, to=orm['track.TrackedWayDayHistorySnapshot'])),
        ))
        db.send_create_signal(u'track', ['TrackedWayDayHistory'])

        # Adding unique constraint on 'TrackedWayDayHistory', fields ['tracked_way', 'departure_date']
        db.create_unique(u'track_trackedwaydayhistory', ['tracked_way_id', 'departure_date'])

        # Adding model 'TrackedWayDayHistorySnapshot'
        db.create_table(u'track_trackedwaydayhistorysnapshot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history', self.gf('django.db.models.fields.related.ForeignKey')(related_name='snapshots', to=orm['track.TrackedWayDayHistory'])),
            ('made_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('total_places_count', self.gf('django.db.models.fields.IntegerField')()),
            ('snapshot_data', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal(u'track', ['TrackedWayDayHistorySnapshot'])


    def backwards(self, orm):
        # Removing unique constraint on 'TrackedWayDayHistory', fields ['tracked_way', 'departure_date']
        db.delete_unique(u'track_trackedwaydayhistory', ['tracked_way_id', 'departure_date'])

        # Removing unique constraint on 'Way', fields ['station_id_from', 'station_id_to']
        db.delete_unique(u'track_way', ['station_id_from', 'station_id_to'])

        # Deleting model 'Way'
        db.delete_table(u'track_way')

        # Deleting model 'TrackedWay'
        db.delete_table(u'track_trackedway')

        # Deleting model 'TrackedWayDayHistory'
        db.delete_table(u'track_trackedwaydayhistory')

        # Deleting model 'TrackedWayDayHistorySnapshot'
        db.delete_table(u'track_trackedwaydayhistorysnapshot')


    models = {
        u'track.trackedway': {
            'Meta': {'object_name': 'TrackedWay'},
            'days': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)'}),
            'way': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['track.Way']"})
        },
        u'track.trackedwaydayhistory': {
            'Meta': {'unique_together': "(('tracked_way', 'departure_date'),)", 'object_name': 'TrackedWayDayHistory'},
            'departure_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'places_appeared': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'marks_appear'", 'unique': 'True', 'null': 'True', 'to': u"orm['track.TrackedWayDayHistorySnapshot']"}),
            'places_disappeared': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'marks_disappear'", 'unique': 'True', 'null': 'True', 'to': u"orm['track.TrackedWayDayHistorySnapshot']"}),
            'tracked_way': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'histories'", 'to': u"orm['track.TrackedWay']"})
        },
        u'track.trackedwaydayhistorysnapshot': {
            'Meta': {'ordering': "['made_on']", 'object_name': 'TrackedWayDayHistorySnapshot'},
            'history': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'snapshots'", 'to': u"orm['track.TrackedWayDayHistory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'snapshot_data': ('jsonfield.fields.JSONField', [], {}),
            'total_places_count': ('django.db.models.fields.IntegerField', [], {})
        },
        u'track.way': {
            'Meta': {'unique_together': "(('station_id_from', 'station_id_to'),)", 'object_name': 'Way'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'station_from': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'station_id_from': ('django.db.models.fields.IntegerField', [], {}),
            'station_id_to': ('django.db.models.fields.IntegerField', [], {}),
            'station_to': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['track']