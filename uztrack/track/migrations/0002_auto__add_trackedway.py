# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TrackedWay'
        db.create_table(u'track_trackedway', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('way', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['track.Way'])),
            ('days', self.gf('django.db.models.fields.BigIntegerField')(default=None)),
        ))
        db.send_create_signal(u'track', ['TrackedWay'])


    def backwards(self, orm):
        # Deleting model 'TrackedWay'
        db.delete_table(u'track_trackedway')


    models = {
        u'track.trackedway': {
            'Meta': {'object_name': 'TrackedWay'},
            'days': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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