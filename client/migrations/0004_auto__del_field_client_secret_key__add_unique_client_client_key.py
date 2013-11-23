# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Client.secret_key'
        db.delete_column(u'client', 'secret_key')

        # Adding unique constraint on 'Client', fields ['client_key']
        db.create_unique(u'client', ['client_key'])


    def backwards(self, orm):
        # Removing unique constraint on 'Client', fields ['client_key']
        db.delete_unique(u'client', ['client_key'])


        # User chose to not deal with backwards NULL issues for 'Client.secret_key'
        raise RuntimeError("Cannot reverse this migration. 'Client.secret_key' and its values cannot be restored.")

    models = {
        'client.client': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Client', 'db_table': "u'client'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'client_key': ('common.fields.UUID4Field', [], {'unique': 'True', 'max_length': '42', 'db_index': 'True'}),
            'client_type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
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