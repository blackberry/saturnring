# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'VG.created_at'
        db.delete_column(u'ssdfrontend_vg', 'created_at')

        # Deleting field 'VG.updated_at'
        db.delete_column(u'ssdfrontend_vg', 'updated_at')

        # Deleting field 'Target.created_at'
        db.delete_column(u'ssdfrontend_target', 'created_at')

        # Deleting field 'Target.updated_at'
        db.delete_column(u'ssdfrontend_target', 'updated_at')

        # Deleting field 'Provisioner.created_at'
        db.delete_column(u'ssdfrontend_provisioner', 'created_at')

        # Deleting field 'Provisioner.updated_at'
        db.delete_column(u'ssdfrontend_provisioner', 'updated_at')

        # Deleting field 'LV.updated_at'
        db.delete_column(u'ssdfrontend_lv', 'updated_at')

        # Deleting field 'LV.created_at'
        db.delete_column(u'ssdfrontend_lv', 'created_at')

        # Deleting field 'StorageHost.created_at'
        db.delete_column(u'ssdfrontend_storagehost', 'created_at')

        # Deleting field 'StorageHost.updated_at'
        db.delete_column(u'ssdfrontend_storagehost', 'updated_at')


    def backwards(self, orm):
        # Adding field 'VG.created_at'
        db.add_column(u'ssdfrontend_vg', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'VG.updated_at'
        db.add_column(u'ssdfrontend_vg', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Target.created_at'
        raise RuntimeError("Cannot reverse this migration. 'Target.created_at' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Target.created_at'
        db.add_column(u'ssdfrontend_target', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Target.updated_at'
        raise RuntimeError("Cannot reverse this migration. 'Target.updated_at' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Target.updated_at'
        db.add_column(u'ssdfrontend_target', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Provisioner.created_at'
        raise RuntimeError("Cannot reverse this migration. 'Provisioner.created_at' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Provisioner.created_at'
        db.add_column(u'ssdfrontend_provisioner', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Provisioner.updated_at'
        raise RuntimeError("Cannot reverse this migration. 'Provisioner.updated_at' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Provisioner.updated_at'
        db.add_column(u'ssdfrontend_provisioner', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True),
                      keep_default=False)

        # Adding field 'LV.updated_at'
        db.add_column(u'ssdfrontend_lv', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'LV.created_at'
        db.add_column(u'ssdfrontend_lv', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'StorageHost.created_at'
        db.add_column(u'ssdfrontend_storagehost', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'StorageHost.updated_at'
        db.add_column(u'ssdfrontend_storagehost', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)


    models = {
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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ssdfrontend.lv': {
            'Meta': {'object_name': 'LV'},
            'lvname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'lvsize': ('django.db.models.fields.FloatField', [], {}),
            'lvthinmapped': ('django.db.models.fields.FloatField', [], {}),
            'lvuuid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.Target']"}),
            'vg': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.VG']"})
        },
        u'ssdfrontend.provisioner': {
            'Meta': {'object_name': 'Provisioner'},
            'clienthost': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'serviceName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sizeinGB': ('django.db.models.fields.FloatField', [], {})
        },
        u'ssdfrontend.storagehost': {
            'Meta': {'object_name': 'StorageHost'},
            'dnsname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'})
        },
        u'ssdfrontend.target': {
            'Meta': {'object_name': 'Target'},
            'clienthost': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'iqnini': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'iqntar': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'sizeinGB': ('django.db.models.fields.FloatField', [], {}),
            'targethost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"})
        },
        u'ssdfrontend.vg': {
            'Meta': {'object_name': 'VG'},
            'vgfreepe': ('django.db.models.fields.FloatField', [], {}),
            'vghost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"}),
            'vgpesize': ('django.db.models.fields.FloatField', [], {}),
            'vgsize': ('django.db.models.fields.FloatField', [], {}),
            'vgtotalpe': ('django.db.models.fields.FloatField', [], {}),
            'vguuid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        }
    }

    complete_apps = ['ssdfrontend']