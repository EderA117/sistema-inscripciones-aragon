from django.contrib import admin
from django.contrib.sessions.models import Session
from django.utils.html import format_html
from .models import Alumno, Horarios, Inscripcion, Asignatura, Planestudio, Profesor

MAPEO_PLANES_ADMIN = {
    1: "Plan 0082 - ING EN COMPUTACION", 
    2: "Plan 1279 - ING EN COMPUTACION", 
    3: "Plan 2119 - ING EN COMPUTACION", 
}

# ==============================================================================
# ENRUTAMIENTO CORRECTO A STAGING_DB (Para tablas no administradas)
# ==============================================================================

@admin.register(Planestudio)
class PlanestudioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'estado')
    
    def get_queryset(self, request):
        # Obliga al admin a listar usando la base de Staging
        return super().get_queryset(request).using('staging_db')

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellidos')
    search_fields = ('nombre', 'apellidos')

    def get_queryset(self, request):
        return super().get_queryset(request).using('staging_db')

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('cve', 'nombre', 'creditos')
    search_fields = ('cve', 'nombre')

    def get_queryset(self, request):
        return super().get_queryset(request).using('staging_db')

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


# ==============================================================================
# MODELOS TRANSACCIONALES (Base por Defecto)
# ==============================================================================

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('no_cuenta', 'nombre_completo', 'get_plan_estudios', 'status_badge')
    search_fields = ('no_cuenta', 'nombre', 'apellidos')
    list_filter = ('plan_estudio_id',)
    ordering = ('apellidos', 'nombre')
    actions = ['reabrir_panel_inscripcion']

    def nombre_completo(self, obj):
        return format_html(f"<strong>{obj.apellidos}</strong>, {obj.nombre}")
    nombre_completo.short_description = 'Estudiante'

    def get_plan_estudios(self, obj):
        return MAPEO_PLANES_ADMIN.get(obj.plan_estudio_id, f"ID: {obj.plan_estudio_id}")
    get_plan_estudios.short_description = 'Plan Escolar'

    def status_badge(self, obj):
        for s in Session.objects.all():
            data = s.get_decoded()
            if data.get(f'finalizado_{obj.id}') is True:
                return format_html('<span style="background: #f4ebe1; color: #b38453; border: 1px solid #d4a373; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.75rem;">🔒 BLOQUEADO</span>')
        return format_html('<span style="background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.75rem;">🔓 ABIERTO</span>')
    status_badge.short_description = 'Estado'

    @admin.action(description='🔓 Habilitar Modificaciones')
    def reabrir_panel_inscripcion(self, request, queryset):
        todas_las_sesiones = Session.objects.all()
        for alumno in queryset:
            for s in todas_las_sesiones:
                data = s.get_decoded()
                if f'finalizado_{alumno.id}' in data:
                    del data[f'finalizado_{alumno.id}']
                    s.session_data = Session.objects.encode(data)
                    s.save()
        self.message_user(request, f"Control de Acceso: Se removió el candado.")


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('get_alumno', 'get_materia', 'get_grupo', 'fecha_inscripcion')
    search_fields = ('alumno__no_cuenta', 'alumno__apellidos', 'cve_asignatura')

    def get_alumno(self, obj):
        return f"{obj.alumno.apellidos}, {obj.alumno.nombre}" if obj.alumno else "Desconocido"
    get_alumno.short_description = 'Alumno'

    def get_materia(self, obj):
        try:
            asig = Asignatura.objects.using('staging_db').get(cve=obj.cve_asignatura)
            return asig.nombre
        except Asignatura.DoesNotExist:
            return f"Clave: {obj.cve_asignatura}"
    get_materia.short_description = 'Materia'

    def get_grupo(self, obj):
        return format_html(f"<code style='background:#1e293b; color:#fff; padding:2px 6px; border-radius:4px;'>Gpo {obj.horarios.grupo}</code>") if obj.horarios else "N/A"
    get_grupo.short_description = 'Grupo'


@admin.register(Horarios)
class HorariosAdmin(admin.ModelAdmin):
    list_display = ('cve_asignatura', 'get_materia_name', 'grupo', 'salon', 'cupo_critico')
    search_fields = ('cve_asignatura', 'grupo')

    def get_materia_name(self, obj):
        try:
            asig = Asignatura.objects.using('staging_db').get(cve=obj.cve_asignatura)
            return asig.nombre
        except Asignatura.DoesNotExist:
            return "No en catálogo"
    get_materia_name.short_description = 'Asignatura'

    def cupo_critico(self, obj):
        if obj.cupo == 0:
            return format_html("<span style='color:#ef4444; font-weight:bold;'>🚫 SIN CUPO</span>")
        return format_html(f"<span style='color:#10b981; font-weight:bold;'>{obj.cupo} lugares</span>")
    cupo_critico.short_description = 'Disponibilidad'