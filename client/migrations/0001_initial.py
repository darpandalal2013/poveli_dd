# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Client'
        db.create_table(u'client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255, null=True, blank=True)),
            ('client_type', self.gf('django.db.models.fields.CharField')(max_length=1, db_index=True)),
            ('secret_key', self.gf('common.fields.UUID4Field')(unique=True, max_length=42, db_index=True)),
        ))
        db.send_create_signal('client', ['Client'])

        # Adding model 'ClientAsset'
        db.create_table(u'client_asset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['client.Client'])),
            ('asset_type', self.gf('django.db.models.fields.CharField')(max_length=1, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('asset', self.gf('django.db.models.fields.files.FileField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('client', ['ClientAsset'])

        # Adding unique constraint on 'ClientAsset', fields ['client', 'name']
        db.create_unique(u'client_asset', ['client_id', 'name'])

        # Adding unique constraint on 'ClientAsset', fields ['client', 'asset']
        db.create_unique(u'client_asset', ['client_id', 'asset'])


    def backwards(self, orm):
        # Removing unique constraint on 'ClientAsset', fields ['client', 'asset']
        db.delete_unique(u'client_asset', ['client_id', 'asset'])

        # Removing unique constraint on 'ClientAsset', fields ['client', 'name']
        db.delete_unique(u'client_asset', ['client_id', 'name'])

        # Deleting model 'Client'
        db.delete_table(u'client')

        # Deleting model 'ClientAsset'
        db.delete_table(u'client_asset')


    models = {
        'client.client': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Client', 'db_table': "u'client'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
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