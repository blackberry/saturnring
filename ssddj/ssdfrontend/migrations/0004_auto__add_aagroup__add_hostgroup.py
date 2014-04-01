# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AAGroup'
        db.create_table(u'ssdfrontend_aagroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'ssdfrontend', ['AAGroup'])

        # Adding model 'HostGroup'
        db.create_table(u'ssdfrontend_hostgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.StorageHost'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.AAGroup'])),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'ssdfrontend', ['HostGroup'])


    def backwards(self, orm):
        # Deleting model 'AAGroup'
        db.delete_table(u'ssdfrontend_aagroup')

        # Deleting model 'HostGroup'
        db.delete_table(u'ssdfrontend_hostgroup')


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
        u'ssdfrontend.aagroup': {
            'Meta': {'object_name': 'AAGroup'},
            'hosts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ssdfrontend.StorageHost']", 'through': u"orm['ssdfrontend.HostGroup']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ssdfrontend.hostgroup': {
            'Meta': {'object_name': 'HostGroup'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.AAGroup']"}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ssdfrontend.lv': {
            'Meta': {'object_name': 'LV'},
            'lvname': ('django.db.models.fields.CharField', [], {'default': "'Not found'", 'max_length': '50'}),
            'lvsize': ('django.db.models.fields.FloatField', [], {}),
            'lvthinmapped': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
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
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ipaddress': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '39'}),
            'storageip1': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '39'}),
            'storageip2': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '39'})
        },
        u'ssdfrontend.target': {
            'Meta': {'object_name': 'Target'},
            'clienthost': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'iqnini': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'iqntar': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'sizeinGB': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'targethost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"})
        },
        u'ssdfrontend.vg': {
            'CurrentAllocGB': ('django.db.models.fields.FloatField', [], {'default': '-100.0'}),
            'Meta': {'object_name': 'VG'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'maxthinavlGB': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
            'opf': ('django.db.models.fields.FloatField', [], {'default': '0.7'}),
            'thintotalGB': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
            'thinusedmaxpercent': ('django.db.models.fields.FloatField', [], {'default': '70'}),
            'thinusedpercent': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
            'vgfreepe': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
            'vghost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"}),
            'vgpesize': ('django.db.models.fields.FloatField', [], {}),
            'vgsize': ('django.db.models.fields.FloatField', [], {}),
            'vgtotalpe': ('django.db.models.fields.FloatField', [], {}),
            'vguuid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        }
    }

    complete_apps = ['ssdfrontend']