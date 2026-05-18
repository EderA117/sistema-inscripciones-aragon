from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_alumno, name='login_alumno'),
    # Ruta para el panel web del alumno (ej. /panel/1/)
    path('panel/<int:alumno_id>/', views.panel_inscripcion, name='panel_inscripcion'),
    
    # Endpoint JSON que usará JavaScript para cargar los grupos en el modal
    path('api/materias/<str:cve_materia>/grupos/', views.api_grupos_materia, name='api_grupos_materia'),

    path('api/inscripcion/apartar/', views.api_apartar_materia, name='api_apartar_materia'),
    path('api/inscripcion/eliminar/<int:inscripcion_id>/', views.api_eliminar_apartado, name='api_eliminar_apartado'),
    path('panel/<int:alumno_id>/comprobante/', views.comprobante_horario, name='comprobante_horario'),
    path('logout/', views.logout_alumno, name='logout_alumno'),
    path('panel/<int:alumno_id>/finalizar/', views.procesar_finalizacion, name='procesar_finalizacion'),
]