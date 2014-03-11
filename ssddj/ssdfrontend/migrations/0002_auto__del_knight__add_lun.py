# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Knight'
        db.delete_table(u'ssdfrontend_knight')

        # Adding model 'Lun'
        db.create_table(u'ssdfrontend_lun', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('iqnname', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'ssdfrontend', ['Lun'])


    def backwards(self, orm):
        # Adding model 'Knight'
        db.create_table(u'ssdfrontend_knight', (
            ('of_the_round_table', self.gf('django.db.models.fields.BooleanField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'ssdfrontend', ['Knight'])

        # Deleting model 'Lun'
        db.delete_table(u'ssdfrontend_lun')


    models = {
        u'ssdfrontend.lun': {
            'Meta': {'object_name': 'Lun'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iqnname': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['ssdfrontend']