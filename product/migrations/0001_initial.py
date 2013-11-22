# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Product'
        db.create_table(u'product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('upc', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('internet_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('image_external', self.gf('django.db.models.fields.URLField')(max_length=512, blank=True)),
        ))
        db.send_create_signal('product', ['Product'])

        # Adding model 'ProductListing'
        db.create_table(u'product_listing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='product_listings', to=orm['client.Client'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'])),
            ('multipack_code', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('retail', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=10, decimal_places=2)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('product', ['ProductListing'])

        # Adding unique constraint on 'ProductListing', fields ['client', 'product', 'multipack_code', 'unit']
        db.create_unique(u'product_listing', ['client_id', 'product_id', 'multipack_code', 'unit'])


    def backwards(self, orm):
        # Removing unique constraint on 'ProductListing', fields ['client', 'product', 'multipack_code', 'unit']
        db.delete_unique(u'product_listing', ['client_id', 'product_id', 'multipack_code', 'unit'])

        # Deleting model 'Product'
        db.delete_table(u'product')

        # Deleting model 'ProductListing'
        db.delete_table(u'product_listing')


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
        'product.product': {
            'Meta': {'object_name': 'Product', 'db_table': "u'product'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'image_external': ('django.db.models.fields.URLField', [], {'max_length': '512', 'blank': 'True'}),
            'internet_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'upc': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'product.productlisting': {
            'Meta': {'unique_together': "(('client', 'product', 'multipack_code', 'unit'),)", 'object_name': 'ProductListing', 'db_table': "u'product_listing'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'product_listings'", 'to': "orm['client.Client']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'multipack_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'retail': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['product']