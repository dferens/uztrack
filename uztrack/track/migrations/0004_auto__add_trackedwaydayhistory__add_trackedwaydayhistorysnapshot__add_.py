# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TrackedWayDayHistory'
        db.create_table(u'track_trackedwaydayhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tracked_way', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['track.TrackedWay'])),
            ('arrival_date', self.gf('django.db.models.fields.DateField')()),
            ('places_appeared', self.gf('django.db.models.fields.related.OneToOneField')(related_name='marks_appear', unique=True, null=True, to=orm['track.TrackedWayDayHistorySnapshot'])),
            ('places_disappeared', self.gf('django.db.models.fields.related.OneToOneField')(related_name='marks_disappear', unique=True, to=orm['track.TrackedWayDayHistorySnapshot'])),
        ))
        db.send_create_signal(u'track', ['TrackedWayDayHistory'])

        # Adding model 'TrackedWayDayHistorySnapshot'
        db.create_table(u'track_trackedwaydayhistorysnapshot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('history', self.gf('django.db.models.fields.related.ForeignKey')(related_name='snapshots', to=orm['track.TrackedWayDayHistory'])),
            ('made_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('total_places_count', self.gf('django.db.models.fields.IntegerField')()),
            ('snapshot_data', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal(u'track', ['TrackedWayDayHistorySnapshot'])

        # Adding unique constraint on 'TrackedWay', fields ['start_time', 'days', 'way']
        db.create_unique(u'track_trackedway', ['start_time', 'days', 'way_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'TrackedWay', fields ['start_time', 'days', 'way']
        db.delete_unique(u'track_trackedway', ['start_time', 'days', 'way_id'])

        # Deleting model 'TrackedWayDayHistory'
        db.delete_table(u'track_trackedwaydayhistory')

        # Deleting model 'TrackedWayDayHistorySnapshot'
        db.delete_table(u'track_trackedwaydayhistorysnapshot')


    models = {
        u'track.trackedway': {
            'Meta': {'unique_together': "(('way', 'days', 'start_time'),)", 'object_name': 'TrackedWay'},
            'days': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)'}),
            'way': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['track.Way']"})
        },
        u'track.trackedwaydayhistory': {
            'Meta': {'object_name': 'TrackedWayDayHistory'},
            'arrival_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'places_appeared': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'marks_appear'", 'unique': 'True', 'null': 'True', 'to': u"orm['track.TrackedWayDayHistorySnapshot']"}),
            'places_disappeared': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'marks_disappear'", 'unique': 'True', 'to': u"orm['track.TrackedWayDayHistorySnapshot']"}),
            'tracked_way': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['track.TrackedWay']"})
        },
        u'track.trackedwaydayhistorysnapshot': {
            'Meta': {'object_name': 'TrackedWayDayHistorySnapshot'},
            'history': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'snapshots'", 'to': u"orm['track.TrackedWayDayHistory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'snapshot_data': ('jsonfield.fields.JSONField', [], {}),
            'total_places_count': ('django.db.models.fields.IntegerField', [], {})
        },
        u'track.way': {
            'Meta': {'unique_together': "(('station_from_id', 'station_till_id'),)", 'object_name': 'Way'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'station_from': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'station_from_id': ('django.db.models.fields.IntegerField', [], {}),
            'station_till': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'station_till_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['track']