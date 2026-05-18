# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Alumno(models.Model):
    no_cuenta = models.CharField(unique=True, blank=True, null=True)
    nombre = models.CharField(blank=True, null=True)
    apellidos = models.CharField(blank=True, null=True)
    plan_estudio_id = models.IntegerField(blank=True, null=True)
    correo = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    contrasena = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.apellidos}, {self.nombre}"

    class Meta:
        managed = False
        db_table = 'Alumno'


class Horarios(models.Model):
    profesor_id = models.IntegerField(blank=True, null=True)
    cve_asignatura = models.CharField(blank=True, null=True)
    grupo = models.CharField(blank=True, null=True)
    tipo = models.CharField(blank=True, null=True)
    lunmarmiejueviesab = models.CharField(db_column='LunMarMieJueVieSab', blank=True, null=True)  # Field name made lowercase.
    salon = models.CharField(blank=True, null=True)
    cupo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Horarios'


class Inscripcion(models.Model):
    alumno = models.ForeignKey(Alumno, models.DO_NOTHING, blank=True, null=True)
    horarios = models.ForeignKey(Horarios, models.DO_NOTHING, db_column='Horarios_id', blank=True, null=True)  # Field name made lowercase.
    cve_asignatura = models.CharField(blank=True, null=True)
    fecha_inscripcion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Inscripcion'
        unique_together = (('alumno', 'cve_asignatura'),)
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Asignatura(models.Model):
    cve = models.CharField(primary_key=True)
    nombre = models.CharField(blank=True, null=True)
    creditos = models.IntegerField(blank=True, null=True)
    plan_estudio = models.ForeignKey('Planestudio', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Asignatura'


class Planestudio(models.Model):
    nombre = models.CharField(blank=True, null=True)
    estado = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PlanEstudio'


class Profesor(models.Model):
    num_empleado = models.CharField(unique=True, blank=True, null=True)
    nombre = models.CharField(blank=True, null=True)
    apellidos = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Profesor'
