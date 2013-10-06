# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TrackedWay.start_time'
        db.add_column(u'track_trackedway', 'start_time',
                      self.gf('django.db.models.fields.TimeField')(default=datetime.time(0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TrackedWay.start_time'
        db.delete_column(u'track_trackedway', 'start_time')


    models = {
        u'track.trackedway': {
            'Meta': {'object_name': 'TrackedWay'},
            'days': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)'}),
            'way': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['track.Way']"})
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