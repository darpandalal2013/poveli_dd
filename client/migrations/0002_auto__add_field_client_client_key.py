# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Client.client_key'
        db.add_column(u'client', 'client_key',
                      self.gf('common.fields.UUID4Field')(db_index=True, default='', max_length=42, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Client.client_key'
        db.delete_column(u'client', 'client_key')


    models = {
        'client.client': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Client', 'db_table': "u'client'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'client_key': ('common.fields.UUID4Field', [], {'db_index': 'True', 'max_length': '42', 'blank': 'True'}),
            'client_type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'secret_key': ('common.fields.UUID4Field', [], {'unique': 'True', 'max_length': '42', 'db_index': 'True'})
        },
        'client.clientasset': {
            'Meta': {'unique_together': "(('client', 'name'), ('client', 'asset'))", 'object_name': 'ClientAsset', 'db_table': "u'client_asset'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'asset': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'blank': 'True'}),
            'asset_type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['client.Client']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['client']