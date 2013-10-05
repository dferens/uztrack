# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Way'
        db.create_table(u'track_way', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station_from', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('station_till', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('station_from_id', self.gf('django.db.models.fields.IntegerField')()),
            ('station_till_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'track', ['Way'])

        # Adding unique constraint on 'Way', fields ['station_from_id', 'station_till_id']
        db.create_unique(u'track_way', ['station_from_id', 'station_till_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Way', fields ['station_from_id', 'station_till_id']
        db.delete_unique(u'track_way', ['station_from_id', 'station_till_id'])

        # Deleting model 'Way'
        db.delete_table(u'track_way')


    models = {
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