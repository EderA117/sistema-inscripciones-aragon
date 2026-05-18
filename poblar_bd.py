import os
import django
import csv
from datetime import datetime

# Configurar el entorno de Django para poder usar los modelos desde este script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_fes_aragon.settings')
django.setup()

# Importar los modelos que creamos
from inscripciones.models import Asignatura, Alumno, Profesor, Grupo
from django.utils import timezone

def poblar_asignaturas():
    print("Poblando Asignaturas...")
    # Ajusta el nombre exacto del archivo
    with open('datos/inscripciones.xlsx - Asignatura.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # get_or_create evita que se dupliquen si corres el script varias veces
            Asignatura.objects.get_or_create(
                clave=row['clave'], 
                defaults={
                    'nombre': row['nombre'],
                    'creditos': int(row['creditos']),
                    'lab': row.get('lab', 'False').strip().lower() in ['true', '1', 'sí', 'si', 'v'],
                    'obl': row.get('obl', 'True').strip().lower() in ['true', '1', 'sí', 'si', 'v'],
                    'semestre': int(row.get('semestre', 1))
                }
            )

def poblar_alumnos():
    print("Poblando Alumnos...")
    with open('datos/inscripciones.xlsx - Alumno.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Simulamos una hora de acceso si el CSV no la tiene aún
            hora_str = row.get('hora_acceso', '2026-08-10 10:00:00') 
            hora_obj = datetime.strptime(hora_str, '%Y-%m-%d %H:%M:%S')

            Alumno.objects.get_or_create(
                correo_ins=row['correo_ins'],
                defaults={
                    'nombre': row['nombre'],
                    'apellido_paterno': row['apellido_paterno'],
                    'apellido_materno': row.get('apellido_materno', ''),
                    'estatus_academico': row.get('estatus_academico', 'True').strip().lower() in ['true', '1', 'activo'],
                    'semestre_actual': int(row.get('semestre_actual', 1)),
                    'hora_acceso': timezone.make_aware(hora_obj)
                }
            )

if __name__ == '__main__':
    poblar_asignaturas()
    poblar_alumnos()
    print("¡Base de datos poblada con éxito!")