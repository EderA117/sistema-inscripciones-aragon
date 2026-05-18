from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
import json
from .models import Alumno, Asignatura, Inscripcion, Horarios, Profesor

def login_alumno(request):
    if request.method == 'POST':
        correo_input = request.POST.get('correo', '').strip().lower()
        password_input = request.POST.get('contrasena', '').strip()
        
                
        try:
            alumno = Alumno.objects.get(correo=correo_input)
            
            # Verificamos el hash
            if check_password(password_input, alumno.contrasena):                
                # Guardamos en la sesión el ID (llave primaria de la BD)
                request.session['alumno_id'] = alumno.id
                request.session.set_expiry(1200)
                
                # REVISIÓN DE REDIRECCIÓN: Ver a dónde lo manda
                if request.session.get(f'finalizado_{alumno.id}') is True:
                    return redirect('comprobante_horario', alumno_id=alumno.id)
                
                return redirect('panel_inscripcion', alumno_id=alumno.id)
            else:
                messages.error(request, "La contraseña ingresada es incorrecta.")
                
        except Alumno.DoesNotExist:
            print("--> ERROR: El correo no existe en la Base de Datos")
            messages.error(request, "El correo institucional no está registrado.")
            
    return render(request, 'inscripciones/login.html')


def panel_inscripcion(request, alumno_id):
    if request.session.get('alumno_id') != alumno_id:
        return redirect('login_alumno')
        
    # El bloqueo ahora depende puramente de la sesión. Si el Admin la borra, el panel se abre
    if request.session.get(f'finalizado_{alumno_id}') is True:
        return redirect('comprobante_horario', alumno_id=alumno_id)
        
    alumno = get_object_or_404(Alumno, id=alumno_id)
    
    # Filtro de 5to semestre que ya tenías
    claves_5to = list(Horarios.objects.filter(grupo__gte='2500', grupo__lte='2599').values_list('cve_asignatura', flat=True).distinct())
    materias_disponibles = Asignatura.objects.using('staging_db').filter(cve__in=claves_5to)
    
    # ¡AQUÍ ESTÁ LA MAGIA! Recuperamos lo que ya tiene en la BD y se lo pintamos en el carrito
    inscripciones_db = Inscripcion.objects.filter(alumno=alumno)
    carrito = []
    materias_apartadas_ids = []
    
    for item in inscripciones_db:
        materias_apartadas_ids.append(item.cve_asignatura)
        try:
            asig = Asignatura.objects.using('staging_db').get(cve=item.cve_asignatura)
            nombre_materia = asig.nombre
        except Asignatura.DoesNotExist:
            nombre_materia = "Asignatura Desconocida"
            
        nombre_profesor = "Sin Profesor asignado"
        if item.horarios and item.horarios.profesor_id:
            try:
                prof = Profesor.objects.using('staging_db').get(id=item.horarios.profesor_id)
                nombre_profesor = f"{prof.nombre} {prof.apellidos}"
            except Profesor.DoesNotExist:
                pass
                
        carrito.append({
            'id_inscripcion': item.id,
            'cve_asignatura': item.cve_asignatura,
            'materia_nombre': nombre_materia,
            'profesor_nombre': nombre_profesor,
            'grupo': item.horarios.grupo if item.horarios else "N/A"
        })

    contexto = {
        'alumno': alumno,
        'materias': materias_disponibles,
        'carrito': carrito,
        'materias_apartadas_ids': materias_apartadas_ids,
    }
    return render(request, 'inscripciones/panel.html', contexto)


def procesar_finalizacion(request, alumno_id):
    if request.method == 'POST' and request.session.get('alumno_id') == alumno_id:
        request.session[f'finalizado_{alumno_id}'] = True
        request.session.modified = True
        return redirect('comprobante_horario', alumno_id=alumno_id)
    return redirect('login_alumno')


def comprobante_horario(request, alumno_id):
    if request.session.get('alumno_id') != alumno_id:
        return redirect('login_alumno')
        
    alumno = get_object_or_404(Alumno, id=alumno_id)
    inscripciones_db = Inscripcion.objects.filter(alumno=alumno)
    
    # Si intenta entrar al comprobante por URL pero no tiene nada, al panel
    if not inscripciones_db.exists() and request.session.get(f'finalizado_{alumno_id}') is not True:
        return redirect('panel_inscripcion', alumno_id=alumno_id)
        
    MAPEO_PLANES = {
        1: "Plan 0082 - ING EN COMPUTACION", 
        2: "Plan 1279 - ING EN COMPUTACION", 
        3: "Plan 2119 - ING EN COMPUTACION", 
    }
    nombre_plan_oficial = MAPEO_PLANES.get(alumno.plan_estudio_id, f"Plan ID: {alumno.plan_estudio_id}")
    
    horario_tabla = []
    for item in inscripciones_db:
        try:
            asig = Asignatura.objects.using('staging_db').get(cve=item.cve_asignatura)
            nombre_materia = asig.nombre
        except Asignatura.DoesNotExist:
            nombre_materia = "Asignatura Desconocida"
            
        nombre_profesor = "Por asignar"
        if item.horarios and item.horarios.profesor_id:
            try:
                prof = Profesor.objects.using('staging_db').get(id=item.horarios.profesor_id)
                nombre_profesor = f"{prof.nombre} {prof.apellidos}"
            except Profesor.DoesNotExist:
                pass
                
        horario_tabla.append({
            'cve': item.cve_asignatura,
            'materia': nombre_materia,
            'grupo': item.horarios.grupo if item.horarios else 'N/A',
            'profesor': nombre_profesor,
            'salon': item.horarios.salon if item.horarios else 'N/A',
            'dias_horas': item.horarios.lunmarmiejueviesab if item.horarios else 'No especificado'
        })
        
    contexto = {
        'alumno': alumno,
        'horario_tabla': horario_tabla,
        'fecha_comprobante': timezone.now(),
        'nombre_plan_oficial': nombre_plan_oficial
    }
    return render(request, 'inscripciones/comprobante.html', contexto)


def logout_alumno(request):
    if 'alumno_id' in request.session:
        del request.session['alumno_id']
    messages.success(request, "Sesión cerrada. Tu horario definitivo sigue bloqueado y resguardado.")
    return redirect('login_alumno')


# 5. ENDPOINTS API ASÍNCRONOS (CONCURRENCIA)
def api_grupos_materia(request, cve_materia):
    # Aplicamos filtro SQL usando el ORM de Django:
    # grupo__gte='2500' significa (grupo >= '2500')
    # grupo__lte='2599' significa (grupo <= '2599')
    horarios_bloque = Horarios.objects.filter(
        cve_asignatura=cve_materia,
        grupo__gte='2500',
        grupo__lte='2599'
    )
    
    lista_grupos = []
    for h in horarios_bloque:
        profesor_nombre = "Sin Profesor"
        if h.profesor_id:
            try:
                p = Profesor.objects.using('staging_db').get(id=h.profesor_id)
                profesor_nombre = f"{p.nombre} {p.apellidos}"
            except Profesor.DoesNotExist:
                pass
                
        texto_horario = f"{h.lunmarmiejueviesab} en Salón: {h.salon}"
        lista_grupos.append({
            'id_horario': h.id,
            'grupo': h.grupo,
            'profesor': profesor_nombre,
            'cupo_total': h.cupo,
            'horarios': [texto_horario]
        })
        
    return JsonResponse({'grupos': lista_grupos})


@csrf_exempt
def api_apartar_materia(request):
    if request.method == 'POST':
        try:
            datos = json.loads(request.body)
            alumno_id = datos.get('alumno_id')
            horario_id = datos.get('horario_id')
            with transaction.atomic():
                alumno = Alumno.objects.get(id=alumno_id)
                horario = Horarios.objects.select_for_update().get(id=horario_id)
                
                ya_inscrita = Inscripcion.objects.filter(alumno=alumno, cve_asignatura=horario.cve_asignatura).exists()
                if ya_inscrita:
                    return JsonResponse({'success': False, 'message': 'Ya tienes esta asignatura apartada.'}, status=400)
                if horario.cupo <= 0:
                    return JsonResponse({'success': False, 'message': f'¡Sin cupos en el grupo {horario.grupo}!'}, status=400)
                    
                horario.cupo -= 1
                horario.save()
                nueva_inscripcion = Inscripcion.objects.create(
                    alumno=alumno, horarios=horario, cve_asignatura=horario.cve_asignatura, fecha_inscripcion=timezone.now()
                )
            try:
                asig = Asignatura.objects.using('staging_db').get(cve=horario.cve_asignatura)
                materia_nombre = asig.nombre
            except Asignatura.DoesNotExist:
                materia_nombre = horario.cve_asignatura
            profesor_nombre = "Sin Profesor"
            if horario.profesor_id:
                try:
                    p = Profesor.objects.using('staging_db').get(id=horario.profesor_id)
                    profesor_nombre = f"{p.nombre} {p.apellidos}"
                except Profesor.DoesNotExist:
                    pass
            return JsonResponse({
                'success': True, 'message': 'Materia apartada con éxito.', 'id_inscripcion': nueva_inscripcion.id,
                'cve_asignatura': horario.cve_asignatura, 'materia_nombre': materia_nombre, 'profesor_nombre': profesor_nombre,
                'grupo': horario.grupo, 'nuevo_cupo': horario.cupo
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
def api_eliminar_apartado(request, inscripcion_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
                cve_liberada = inscripcion.cve_asignatura
                if inscripcion.horarios:
                    horario = Horarios.objects.select_for_update().get(id=inscripcion.horarios.id)
                    horario.cupo += 1
                    horario.save()
                inscripcion.delete()
            return JsonResponse({'success': True, 'message': 'Cupo liberado.', 'cve_asignatura': cve_liberada})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

