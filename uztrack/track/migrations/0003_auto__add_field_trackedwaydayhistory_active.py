# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TrackedWayDayHistory.active'
        db.add_column(u'track_trackedwaydayhistory', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TrackedWayDayHistory.active'
        db.delete_column(u'track_trackedwaydayhistory', 'active')


    models = {
        u'accounts.profile': {
            'Meta': {'object_name': 'Profile'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'track.trackedway': {
            'Meta': {'object_name': 'TrackedWay'},
            'days': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Profile']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)'}),
            'way': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['track.Way']"})
        },
        u'track.trackedwaydayhistory': {
            'Meta': {'ordering': "['departure_date']", 'unique_together': "(('tracked_way', 'departure_date'),)", 'object_name': 'TrackedWayDayHistory'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'departure_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'places_appeared': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'marks_appear'", 'unique': 'True', 'null': 'True', 'to': u"orm['track.TrackedWayDayHistorySnapshot']"}),
            'places_disappeared': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'marks_disappear'", 'unique': 'True', 'null': 'True', 'to': u"orm['track.TrackedWayDayHistorySnapshot']"}),
            'tracked_way': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'histories'", 'to': u"orm['track.TrackedWay']"})
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
            'Meta': {'unique_together': "(('station_id_from', 'station_id_to'),)", 'object_name': 'Way'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'station_from': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'station_id_from': ('django.db.models.fields.IntegerField', [], {}),
            'station_id_to': ('django.db.models.fields.IntegerField', [], {}),
            'station_to': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['track']