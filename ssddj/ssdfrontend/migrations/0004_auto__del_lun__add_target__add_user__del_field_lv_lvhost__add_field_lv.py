# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Lun'
        db.delete_table(u'ssdfrontend_lun')

        # Adding model 'Target'
        db.create_table(u'ssdfrontend_target', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.User'])),
            ('iqnini', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('iqntar', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'ssdfrontend', ['Target'])

        # Adding model 'User'
        db.create_table(u'ssdfrontend_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('loginname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'ssdfrontend', ['User'])

        # Deleting field 'LV.lvhost'
        db.delete_column(u'ssdfrontend_lv', 'lvhost_id')

        # Adding field 'LV.target'
        db.add_column(u'ssdfrontend_lv', 'target',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['ssdfrontend.Target']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'Lun'
        db.create_table(u'ssdfrontend_lun', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('iqnname', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'ssdfrontend', ['Lun'])

        # Deleting model 'Target'
        db.delete_table(u'ssdfrontend_target')

        # Deleting model 'User'
        db.delete_table(u'ssdfrontend_user')

        # Adding field 'LV.lvhost'
        db.add_column(u'ssdfrontend_lv', 'lvhost',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['ssdfrontend.StorageHost']),
                      keep_default=False)

        # Deleting field 'LV.target'
        db.delete_column(u'ssdfrontend_lv', 'target_id')


    models = {
        u'ssdfrontend.lv': {
            'Meta': {'object_name': 'LV'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lvname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'lvsize': ('django.db.models.fields.FloatField', [], {}),
            'lvthin': ('django.db.models.fields.BooleanField', [], {}),
            'lvthinused': ('django.db.models.fields.FloatField', [], {}),
            'lvuuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.Target']"}),
            'vg': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.VG']"})
        },
        u'ssdfrontend.storagehost': {
            'Meta': {'object_name': 'StorageHost'},
            'dnsname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'})
        },
        u'ssdfrontend.target': {
            'Meta': {'object_name': 'Target'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iqnini': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'iqntar': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.User']"})
        },
        u'ssdfrontend.user': {
            'Meta': {'object_name': 'User'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loginname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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