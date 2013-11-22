# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LabelTemplate'
        db.create_table(u'label_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='label_templates', to=orm['client.Client'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('size', self.gf('django.db.models.fields.CharField')(default='264x176', max_length=20)),
            ('bg_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('title_pos', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('title_font', self.gf('django.db.models.fields.CharField')(default='arial.ttf', max_length=100, blank=True)),
            ('title_font_size', self.gf('django.db.models.fields.IntegerField')(default='12', blank=True)),
            ('desc_pos', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('desc_font', self.gf('django.db.models.fields.CharField')(default='arial.ttf', max_length=100, blank=True)),
            ('desc_font_size', self.gf('django.db.models.fields.IntegerField')(default='10', blank=True)),
            ('retail_pos', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('retail_font', self.gf('django.db.models.fields.CharField')(default='arial.ttf', max_length=100, blank=True)),
            ('retail_font_size', self.gf('django.db.models.fields.IntegerField')(default='28', blank=True)),
            ('pic_pos', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('label', ['LabelTemplate'])

        # Adding unique constraint on 'LabelTemplate', fields ['client', 'title']
        db.create_unique(u'label_template', ['client_id', 'title'])

        # Adding model 'Label'
        db.create_table(u'label', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='labels', to=orm['client.Client'])),
            ('upc', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('size', self.gf('django.db.models.fields.CharField')(default='264x176', max_length=20)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['label.LabelTemplate'])),
            ('product_listing', self.gf('django.db.models.fields.related.ForeignKey')(related_name='labels', to=orm['product.ProductListing'])),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('sent_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='NEW', max_length=10)),
            ('fail_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('successfull_host', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('signal_strength', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('label', ['Label'])

        # Adding unique constraint on 'Label', fields ['client', 'upc']
        db.create_unique(u'label', ['client_id', 'upc'])


    def backwards(self, orm):
        # Removing unique constraint on 'Label', fields ['client', 'upc']
        db.delete_unique(u'label', ['client_id', 'upc'])

        # Removing unique constraint on 'LabelTemplate', fields ['client', 'title']
        db.delete_unique(u'label_template', ['client_id', 'title'])

        # Deleting model 'LabelTemplate'
        db.delete_table(u'label_template')

        # Deleting model 'Label'
        db.delete_table(u'label')


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
        'label.label': {
            'Meta': {'unique_together': "(('client', 'upc'),)", 'object_name': 'Label', 'db_table': "u'label'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['client.Client']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'fail_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product_listing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['product.ProductListing']"}),
            'sent_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'signal_strength': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'size': ('django.db.models.fields.CharField', [], {'default': "'264x176'", 'max_length': '20'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '10'}),
            'successfull_host': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['label.LabelTemplate']"}),
            'upc': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'label.labeltemplate': {
            'Meta': {'unique_together': "(('client', 'title'),)", 'object_name': 'LabelTemplate', 'db_table': "u'label_template'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'bg_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'label_templates'", 'to': "orm['client.Client']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'desc_font': ('django.db.models.fields.CharField', [], {'default': "'arial.ttf'", 'max_length': '100', 'blank': 'True'}),
            'desc_font_size': ('django.db.models.fields.IntegerField', [], {'default': "'10'", 'blank': 'True'}),
            'desc_pos': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pic_pos': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'retail_font': ('django.db.models.fields.CharField', [], {'default': "'arial.ttf'", 'max_length': '100', 'blank': 'True'}),
            'retail_font_size': ('django.db.models.fields.IntegerField', [], {'default': "'28'", 'blank': 'True'}),
            'retail_pos': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'default': "'264x176'", 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title_font': ('django.db.models.fields.CharField', [], {'default': "'arial.ttf'", 'max_length': '100', 'blank': 'True'}),
            'title_font_size': ('django.db.models.fields.IntegerField', [], {'default': "'12'", 'blank': 'True'}),
            'title_pos': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
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

    complete_apps = ['label']