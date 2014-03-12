# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VG'
        db.create_table(u'ssdfrontend_vg', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vghost', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.StorageHost'])),
            ('vgsize', self.gf('django.db.models.fields.FloatField')()),
            ('vguuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('vgpesize', self.gf('django.db.models.fields.IntegerField')()),
            ('vgtotalpe', self.gf('django.db.models.fields.IntegerField')()),
            ('vgfreepe', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'ssdfrontend', ['VG'])

        # Adding model 'LV'
        db.create_table(u'ssdfrontend_lv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lvhost', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.StorageHost'])),
            ('vg', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.VG'])),
            ('lvname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('lvsize', self.gf('django.db.models.fields.FloatField')()),
            ('lvuuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('lvthin', self.gf('django.db.models.fields.BooleanField')()),
            ('lvthinused', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'ssdfrontend', ['LV'])

        # Adding model 'StorageHost'
        db.create_table(u'ssdfrontend_storagehost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dnsname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('ipaddress', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39)),
        ))
        db.send_create_signal(u'ssdfrontend', ['StorageHost'])


    def backwards(self, orm):
        # Deleting model 'VG'
        db.delete_table(u'ssdfrontend_vg')

        # Deleting model 'LV'
        db.delete_table(u'ssdfrontend_lv')

        # Deleting model 'StorageHost'
        db.delete_table(u'ssdfrontend_storagehost')


    models = {
        u'ssdfrontend.lun': {
            'Meta': {'object_name': 'Lun'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iqnname': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ssdfrontend.lv': {
            'Meta': {'object_name': 'LV'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lvhost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"}),
            'lvname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'lvsize': ('django.db.models.fields.FloatField', [], {}),
            'lvthin': ('django.db.models.fields.BooleanField', [], {}),
            'lvthinused': ('django.db.models.fields.FloatField', [], {}),
            'lvuuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'vg': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.VG']"})
        },
        u'ssdfrontend.storagehost': {
            'Meta': {'object_name': 'StorageHost'},
            'dnsname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'})
        },
        u'ssdfrontend.vg': {
            'Meta': {'object_name': 'VG'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vgfreepe': ('django.db.models.fields.IntegerField', [], {}),
            'vghost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"}),
            'vgpesize': ('django.db.models.fields.IntegerField', [], {}),
            'vgsize': ('django.db.models.fields.FloatField', [], {}),
            'vgtotalpe': ('django.db.models.fields.IntegerField', [], {}),
            'vguuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['ssdfrontend']