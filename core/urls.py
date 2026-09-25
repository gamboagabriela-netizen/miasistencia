from django.urls import path
from . import views

urlpatterns = [
    # Inicio y Autenticación
    path("", views.inicio, name="inicio"),
    path("login/", views.login, name="login"),
    path("logout/", views.cerrar_sesion, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Cursos (Nueva funcionalidad)
    path("cursos/", views.cursos, name="cursos"),
    path("cursos/<int:curso_id>/estudiantes/", views.estudiantes_por_curso, name="estudiantes_por_curso"),

    # Estudiantes (Mantenimiento)
    path("estudiantes/", views.estudiantes, name="estudiantes"),
    path("estudiantes/agregar/", views.agregar_estudiante, name="agregar_estudiante"),
    path("estudiantes/descargar-plantilla/", views.descargar_plantilla_estudiantes, name="descargar_plantilla"),
    path("estudiantes/importar/", views.importar_estudiantes, name="importar_estudiantes"),
    path("estudiantes/editar/<int:id>/", views.editar_estudiante, name="editar_estudiante"),
    path("estudiantes/eliminar/<int:id>/", views.eliminar_estudiante, name="eliminar_estudiante"),
    path("estudiantes/historial/<int:id>/", views.historial_estudiante, name="historial_estudiante"),
    path("mi-historial/", views.mi_historial, name="mi_historial"),

    # Docentes
    path("docentes/", views.docentes, name="docentes"),
    path("docentes/agregar/", views.agregar_docente, name="agregar_docente"),
    path("docentes/editar/<int:id>/", views.editar_docente, name="editar_docente"),
    path("docentes/eliminar/<int:id>/", views.eliminar_docente, name="eliminar_docente"),

    # Faltas
    path("faltas/", views.faltas, name="faltas"),
    path("faltas/agregar/", views.agregar_falta, name="agregar_falta"),
    path("faltas/editar/<int:id>/", views.editar_falta, name="editar_falta"),
    path("faltas/eliminar/<int:id>/", views.eliminar_falta, name="eliminar_falta"),
    path("faltas/pendientes/", views.faltas_pendientes, name="faltas_pendientes"),
    path("faltas/revisar/<int:id>/", views.revisar_falta, name="revisar_falta"),
    path("faltas/justificar/<int:id>/", views.justificar_falta, name="justificar_falta"),

    # APIs para búsqueda
    path("api/buscar-estudiantes/", views.api_buscar_estudiantes, name="api_buscar_estudiantes"),
    path("api/cursos-por-grado/", views.api_cursos_por_grado, name="api_cursos_por_grado"),

    # Estadísticas (Nueva funcionalidad)
    path("estadisticas/", views.estadisticas, name="estadisticas"),
    path("estadisticas/curso/<int:curso_id>/", views.estadisticas_curso, name="estadisticas_curso"),

    # Cambio de contraseñas
    path("cambiar-contrasena/", views.cambiar_contrasena_propia, name="cambiar_contrasena_propia"),
    path("estudiantes/<int:id>/cambiar-contrasena/", views.cambiar_contrasena_estudiante, name="cambiar_contrasena_estudiante"),

    # Recuperar contraseña
    path("olvide-contrasena/", views.olvide_contrasena, name="olvide_contrasena"),
    path("solicitudes-contrasena/", views.solicitudes_contrasena, name="solicitudes_contrasena"),
    path("solicitudes-contrasena/<int:id>/atendida/", views.marcar_solicitud_atendida, name="marcar_solicitud_atendida"),
    path("usuarios/<int:id>/restablecer-contrasena/", views.restablecer_contrasena_usuario, name="restablecer_contrasena_usuario"),
]