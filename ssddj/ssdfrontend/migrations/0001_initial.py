# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Provisioner'
        db.create_table(u'ssdfrontend_provisioner', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('clienthost', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sizeinGB', self.gf('django.db.models.fields.FloatField')()),
            ('serviceName', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'ssdfrontend', ['Provisioner'])

        # Adding model 'LV'
        db.create_table(u'ssdfrontend_lv', (
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.Target'])),
            ('vg', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.VG'])),
            ('lvname', self.gf('django.db.models.fields.CharField')(default='Not found', max_length=50)),
            ('lvsize', self.gf('django.db.models.fields.FloatField')()),
            ('lvuuid', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('lvthinmapped', self.gf('django.db.models.fields.FloatField')(default=-1)),
        ))
        db.send_create_signal(u'ssdfrontend', ['LV'])

        # Adding model 'VG'
        db.create_table(u'ssdfrontend_vg', (
            ('vghost', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.StorageHost'])),
            ('vgsize', self.gf('django.db.models.fields.FloatField')()),
            ('vguuid', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('vgpesize', self.gf('django.db.models.fields.FloatField')()),
            ('vgtotalpe', self.gf('django.db.models.fields.FloatField')()),
            ('vgfreepe', self.gf('django.db.models.fields.FloatField')(default=-1)),
            ('thinusedpercent', self.gf('django.db.models.fields.FloatField')(default=-1)),
            ('thintotalGB', self.gf('django.db.models.fields.FloatField')(default=-1)),
            ('maxthinavlGB', self.gf('django.db.models.fields.FloatField')(default=-1)),
            ('opf', self.gf('django.db.models.fields.FloatField')(default=0.7)),
            ('thinusedmaxpercent', self.gf('django.db.models.fields.FloatField')(default=70)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('CurrentAllocGB', self.gf('django.db.models.fields.FloatField')(default=-100.0)),
        ))
        db.send_create_signal(u'ssdfrontend', ['VG'])

        # Adding model 'StorageHost'
        db.create_table(u'ssdfrontend_storagehost', (
            ('dnsname', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('ipaddress', self.gf('django.db.models.fields.GenericIPAddressField')(default='127.0.0.1', max_length=39)),
            ('storageip1', self.gf('django.db.models.fields.GenericIPAddressField')(default='127.0.0.1', max_length=39)),
            ('storageip2', self.gf('django.db.models.fields.GenericIPAddressField')(default='127.0.0.1', max_length=39)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'ssdfrontend', ['StorageHost'])

        # Adding model 'AAGroup'
        db.create_table(u'ssdfrontend_aagroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'ssdfrontend', ['AAGroup'])

        # Adding M2M table for field hosts on 'AAGroup'
        m2m_table_name = db.shorten_name(u'ssdfrontend_aagroup_hosts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aagroup', models.ForeignKey(orm[u'ssdfrontend.aagroup'], null=False)),
            ('storagehost', models.ForeignKey(orm[u'ssdfrontend.storagehost'], null=False))
        ))
        db.create_unique(m2m_table_name, ['aagroup_id', 'storagehost_id'])

        # Adding model 'Target'
        db.create_table(u'ssdfrontend_target', (
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('targethost', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.StorageHost'])),
            ('iqnini', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('iqntar', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('clienthost', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sizeinGB', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('aagroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ssdfrontend.AAGroup'], null=True, blank=True)),
        ))
        db.send_create_signal(u'ssdfrontend', ['Target'])


    def backwards(self, orm):
        # Deleting model 'Provisioner'
        db.delete_table(u'ssdfrontend_provisioner')

        # Deleting model 'LV'
        db.delete_table(u'ssdfrontend_lv')

        # Deleting model 'VG'
        db.delete_table(u'ssdfrontend_vg')

        # Deleting model 'StorageHost'
        db.delete_table(u'ssdfrontend_storagehost')

        # Deleting model 'AAGroup'
        db.delete_table(u'ssdfrontend_aagroup')

        # Removing M2M table for field hosts on 'AAGroup'
        db.delete_table(db.shorten_name(u'ssdfrontend_aagroup_hosts'))

        # Deleting model 'Target'
        db.delete_table(u'ssdfrontend_target')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'aagroup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ssdfrontend.AAGroup']", 'null': 'True', 'blank': 'True'}),
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