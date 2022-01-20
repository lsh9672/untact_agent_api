# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Camera(models.Model):
    cameraid = models.AutoField(db_column='CameraId', primary_key=True)  # Field name made lowercase.
    cameraip = models.BigIntegerField(db_column='CameraIP')  # Field name made lowercase.
    streamport = models.IntegerField(db_column='StreamPort')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Camera'


class Connectionlog(models.Model):
    userid = models.CharField(db_column='UserId', primary_key=True, max_length=60)  # Field name made lowercase.
    equipmentid = models.ForeignKey('Typeofequipment', models.DO_NOTHING, db_column='EquipmentId')  # Field name made lowercase.
    equipmentip = models.ForeignKey('Equipment', models.DO_NOTHING, db_column='EquipmentIP')  # Field name made lowercase.
    entertime = models.DateTimeField(db_column='EnterTime')  # Field name made lowercase.
    finishtime = models.DateTimeField(db_column='FinishTime', blank=True, null=True)  # Field name made lowercase.
    lectureid = models.CharField(db_column='LectureId', max_length=50)  # Field name made lowercase.
    fsid = models.ForeignKey('Filedata', models.DO_NOTHING, db_column='FSID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'ConnectionLog'
        unique_together = (('userid', 'entertime'),)


class Equipment(models.Model):
    equipmentip = models.BigIntegerField(db_column='EquipmentIP', primary_key=True)  # Field name made lowercase.
    equipmentid = models.ForeignKey('Typeofequipment', models.DO_NOTHING, db_column='EquipmentId')  # Field name made lowercase.
    cameraid = models.ForeignKey(Camera, models.DO_NOTHING, db_column='CameraId')  # Field name made lowercase.
    apiport = models.IntegerField(db_column='APIPort')  # Field name made lowercase.
    ideport = models.IntegerField(db_column='IDEPort')  # Field name made lowercase.
    sshport = models.IntegerField(db_column='SSHPort')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Equipment'


class Filedata(models.Model):
    fsid = models.CharField(db_column='FSID', primary_key=True, max_length=36)  # Field name made lowercase.
    filename = models.CharField(db_column='FileName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fsblob = models.BinaryField(db_column='FSBLOB', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'FileData'


class Typeofequipment(models.Model):
    equipmentid = models.AutoField(db_column='EquipmentId', primary_key=True)  # Field name made lowercase.
    equipmentname = models.CharField(db_column='EquipmentName', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'TypeOfEquipment'


class Sysdiagrams(models.Model):
    name = models.CharField(max_length=128)
    principal_id = models.IntegerField()
    diagram_id = models.AutoField(primary_key=True)
    version = models.IntegerField(blank=True, null=True)
    definition = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sysdiagrams'
        unique_together = (('principal_id', 'name'),)
