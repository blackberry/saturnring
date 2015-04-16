# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SnapJob'
        db.create_table(u'ssdfrontend_snapjob', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('numsnaps', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('iqntar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.Target'])),
            ('cronstring', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('lastrun', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('nextrun', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('deleted_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('enqueued', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('run_now', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'ssdfrontend', ['SnapJob'])

        # Deleting field 'VG.thintotalGB'
        db.delete_column(u'ssdfrontend_vg', 'thintotalGB')

        # Deleting field 'VG.thinusedpercent'
        db.delete_column(u'ssdfrontend_vg', 'thinusedpercent')

        # Deleting field 'VG.opf'
        db.delete_column(u'ssdfrontend_vg', 'opf')

        # Deleting field 'VG.maxthinavlGB'
        db.delete_column(u'ssdfrontend_vg', 'maxthinavlGB')

        # Deleting field 'VG.thinusedmaxpercent'
        db.delete_column(u'ssdfrontend_vg', 'thinusedmaxpercent')

        # Adding field 'VG.totalGB'
        db.add_column(u'ssdfrontend_vg', 'totalGB',
                      self.gf('django.db.models.fields.FloatField')(default=-1),
                      keep_default=False)

        # Adding field 'VG.maxavlGB'
        db.add_column(u'ssdfrontend_vg', 'maxavlGB',
                      self.gf('django.db.models.fields.FloatField')(default=-1),
                      keep_default=False)

        # Adding field 'VG.storemedia'
        db.add_column(u'ssdfrontend_vg', 'storemedia',
                      self.gf('django.db.models.fields.CharField')(default='unassigned', max_length=200),
                      keep_default=False)

        # Adding field 'VG.is_thin'
        db.add_column(u'ssdfrontend_vg', 'is_thin',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'StorageHost.snaplock'
        db.add_column(u'ssdfrontend_storagehost', 'snaplock',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'LV.lvthinmapped'
        db.delete_column(u'ssdfrontend_lv', 'lvthinmapped')


    def backwards(self, orm):
        # Deleting model 'SnapJob'
        db.delete_table(u'ssdfrontend_snapjob')

        # Adding field 'VG.thintotalGB'
        db.add_column(u'ssdfrontend_vg', 'thintotalGB',
                      self.gf('django.db.models.fields.FloatField')(default=-1),
                      keep_default=False)

        # Adding field 'VG.thinusedpercent'
        db.add_column(u'ssdfrontend_vg', 'thinusedpercent',
                      self.gf('django.db.models.fields.FloatField')(default=-1),
                      keep_default=False)

        # Adding field 'VG.opf'
        db.add_column(u'ssdfrontend_vg', 'opf',
                      self.gf('django.db.models.fields.FloatField')(default=0.99),
                      keep_default=False)

        # Adding field 'VG.maxthinavlGB'
        db.add_column(u'ssdfrontend_vg', 'maxthinavlGB',
                      self.gf('django.db.models.fields.FloatField')(default=-1),
                      keep_default=False)

        # Adding field 'VG.thinusedmaxpercent'
        db.add_column(u'ssdfrontend_vg', 'thinusedmaxpercent',
                      self.gf('django.db.models.fields.FloatField')(default=99),
                      keep_default=False)

        # Deleting field 'VG.totalGB'
        db.delete_column(u'ssdfrontend_vg', 'totalGB')

        # Deleting field 'VG.maxavlGB'
        db.delete_column(u'ssdfrontend_vg', 'maxavlGB')

        # Deleting field 'VG.storemedia'
        db.delete_column(u'ssdfrontend_vg', 'storemedia')

        # Deleting field 'VG.is_thin'
        db.delete_column(u'ssdfrontend_vg', 'is_thin')

        # Deleting field 'StorageHost.snaplock'
        db.delete_column(u'ssdfrontend_storagehost', 'snaplock')

        # Adding field 'LV.lvthinmapped'
        db.add_column(u'ssdfrontend_lv', 'lvthinmapped',
                      self.gf('django.db.models.fields.FloatField')(default=-1),
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
        u'ssdfrontend.aagroup': {
            'Meta': {'object_name': 'AAGroup'},
            'hosts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ssdfrontend.StorageHost']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.Target']", 'null': 'True', 'blank': 'True'})
        },
        u'ssdfrontend.clumpgroup': {
            'Meta': {'object_name': 'ClumpGroup'},
            'hosts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ssdfrontend.StorageHost']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.Target']", 'null': 'True', 'blank': 'True'})
        },
        u'ssdfrontend.interface': {
            'Meta': {'object_name': 'Interface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'iprange': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ssdfrontend.IPRange']", 'symmetrical': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'storagehost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"})
        },
        u'ssdfrontend.iprange': {
            'Meta': {'object_name': 'IPRange'},
            'hosts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ssdfrontend.StorageHost']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iprange': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'ssdfrontend.lock': {
            'Meta': {'object_name': 'Lock'},
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lockname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        u'ssdfrontend.lv': {
            'Meta': {'object_name': 'LV'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'lvname': ('django.db.models.fields.CharField', [], {'default': "'Not found'", 'max_length': '200'}),
            'lvsize': ('django.db.models.fields.FloatField', [], {}),
            'lvuuid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.Target']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'vg': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.VG']"})
        },
        u'ssdfrontend.profile': {
            'Meta': {'object_name': 'Profile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_alloc_sizeGB': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'max_target_sizeGB': ('django.db.models.fields.FloatField', [], {'default': '5'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'ssdfrontend.provisioner': {
            'Meta': {'object_name': 'Provisioner'},
            'clientiqn': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'serviceName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sizeinGB': ('django.db.models.fields.FloatField', [], {})
        },
        u'ssdfrontend.snapjob': {
            'Meta': {'object_name': 'SnapJob'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cronstring': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'enqueued': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iqntar': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.Target']"}),
            'lastrun': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'nextrun': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'numsnaps': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'run_now': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ssdfrontend.storagehost': {
            'Meta': {'object_name': 'StorageHost'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'dnsname': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ipaddress': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '39'}),
            'snaplock': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'storageip1': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '39'}),
            'storageip2': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '39'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'ssdfrontend.target': {
            'Meta': {'object_name': 'Target'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'iqnini': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'iqntar': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'rkb': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'rkbpm': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'sessionup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sizeinGB': ('django.db.models.fields.FloatField', [], {'max_length': '200'}),
            'storageip1': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '39'}),
            'storageip2': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '39'}),
            'targethost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'wkb': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'wkbpm': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        },
        u'ssdfrontend.targethistory': {
            'Meta': {'object_name': 'TargetHistory'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iqnini': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'iqntar': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'rkb': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'sizeinGB': ('django.db.models.fields.FloatField', [], {'max_length': '200'}),
            'wkb': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        },
        u'ssdfrontend.vg': {
            'CurrentAllocGB': ('django.db.models.fields.FloatField', [], {'default': '-100.0', 'null': 'True'}),
            'Meta': {'object_name': 'VG'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'in_error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_thin': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'maxavlGB': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
            'storemedia': ('django.db.models.fields.CharField', [], {'default': "'unassigned'", 'max_length': '200'}),
            'totalGB': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'vgfreepe': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
            'vghost': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.StorageHost']"}),
            'vgpesize': ('django.db.models.fields.FloatField', [], {}),
            'vgsize': ('django.db.models.fields.FloatField', [], {}),
            'vgtotalpe': ('django.db.models.fields.FloatField', [], {}),
            'vguuid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'})
        }
    }

    complete_apps = ['ssdfrontend']