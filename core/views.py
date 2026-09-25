from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from functools import wraps
import csv
import io

from .models import Estudiante, Docente, Falta, Curso, SolicitudContrasena


def _crear_usuario_estudiante(codigo, contraseña):
    """Crea usuario para estudiante si no existe. Usuario = Código."""
    try:
        if not User.objects.filter(username=codigo).exists():
            usuario = User.objects.create_user(
                username=codigo,
                password=contraseña
            )
            grupo_estudiantes, _ = Group.objects.get_or_create(name="Estudiantes")
            usuario.groups.add(grupo_estudiantes)
    except Exception as e:
        print(f"Error creando usuario para {codigo}: {str(e)}")


def acceso_denegado(request, mensaje):
    messages.error(request, mensaje)
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def requiere_coordinador(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return acceso_denegado(request, "Acceso denegado. Se requieren permisos de coordinador.")
        return view_func(request, *args, **kwargs)
    return wrapper


def requiere_docente(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.groups.filter(name="Docentes").exists():
            return acceso_denegado(request, "Acceso denegado. Se requieren permisos de docente.")
        return view_func(request, *args, **kwargs)
    return wrapper


def requiere_estudiante(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.groups.filter(name="Estudiantes").exists():
            return acceso_denegado(request, "Acceso denegado. Se requieren permisos de estudiante.")
        return view_func(request, *args, **kwargs)
    return wrapper


def inicio(request):
    return render(request, "core/inicio.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        password = request.POST["password"].strip()
        tipo_usuario = request.POST["tipo_usuario"]

        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            if tipo_usuario == "Coordinador" and usuario.is_superuser:
                auth_login(request, usuario)
                return redirect("dashboard")
            elif tipo_usuario == "Docente" and usuario.groups.filter(name="Docentes").exists():
                auth_login(request, usuario)
                return redirect("dashboard")
            elif tipo_usuario == "Estudiante" and usuario.groups.filter(name="Estudiantes").exists():
                auth_login(request, usuario)
                return redirect("dashboard")
            else:
                messages.error(request, "El tipo de usuario seleccionado no corresponde con su cuenta.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "core/login.html")


def cerrar_sesion(request):
    auth_logout(request)
    return redirect("inicio")


@login_required(login_url="login")
def dashboard(request):
    context = {}

    if request.user.is_superuser:
        context['tipo_usuario'] = 'Coordinador'
    elif request.user.groups.filter(name="Docentes").exists():
        context['tipo_usuario'] = 'Docente'
    elif request.user.groups.filter(name="Estudiantes").exists():
        context['tipo_usuario'] = 'Estudiante'

    return render(request, "core/dashboard.html", context)


@login_required(login_url="login")
def cursos(request):
    lista = Curso.objects.all()
    return render(request, "core/cursos.html", {"cursos": lista})


@login_required(login_url="login")
def estudiantes_por_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    estudiantes = Estudiante.objects.filter(curso=curso.nombre).order_by('apellido', 'nombre')
    return render(request, "core/estudiantes_por_curso.html", {
        "curso": curso,
        "estudiantes": estudiantes
    })


@requiere_coordinador
def estudiantes(request):
    lista = Estudiante.objects.all()
    return render(request, "core/estudiantes.html", {"estudiantes": lista})


@requiere_coordinador
def agregar_estudiante(request):
    if request.method == "POST":
        curso = get_object_or_404(Curso, id=request.POST["curso"])
        codigo = request.POST["codigo"]

        if Estudiante.objects.filter(codigo=codigo).exists():
            messages.error(request, f"El código {codigo} ya existe.")
            cursos = Curso.objects.all()
            return render(request, "core/agregar_estudiante.html", {"cursos": cursos})

        estudiante = Estudiante.objects.create(
            codigo=codigo,
            nombre=request.POST["nombre"],
            apellido=request.POST["apellido"],
            curso=curso.nombre
        )

        _crear_usuario_estudiante(codigo, "1234")
        messages.success(request, f"Estudiante {codigo} agregado exitosamente.")
        return redirect("estudiantes")

    cursos = Curso.objects.all()
    return render(request, "core/agregar_estudiante.html", {"cursos": cursos})


@requiere_coordinador
def descargar_plantilla_estudiantes(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="estudiantes_plantilla.csv"'

    writer = csv.writer(response)
    writer.writerow(['codigo', 'nombre', 'apellido', 'grado', 'curso'])
    writer.writerow(['2015000', 'Juan', 'Pérez', '10', '01'])
    writer.writerow(['2015001', 'María', 'García', '10', '02'])

    return response


@requiere_coordinador
def importar_estudiantes(request):
    if request.method == "POST":
        if 'archivo' not in request.FILES:
            messages.error(request, "No se seleccionó archivo.")
            return redirect("estudiantes")

        archivo = request.FILES['archivo']

        if not archivo.name.endswith('.csv'):
            messages.error(request, "El archivo debe ser CSV.")
            return redirect("estudiantes")

        try:
            contenido = archivo.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(contenido))

            exitosos = 0
            errores = 0
            errores_detalle = []

            for row in reader:
                try:
                    codigo = row.get('codigo', '').strip()
                    nombre = row.get('nombre', '').strip()
                    apellido = row.get('apellido', '').strip()
                    grado_str = row.get('grado', '').strip()
                    curso = row.get('curso', '').strip()

                    if not codigo:
                        errores += 1
                        errores_detalle.append("Fila sin código")
                        continue

                    if Estudiante.objects.filter(codigo=codigo).exists():
                        errores += 1
                        errores_detalle.append(f"Código {codigo} duplicado")
                        continue

                    try:
                        grado = int(grado_str)
                    except ValueError:
                        errores += 1
                        errores_detalle.append(f"Grado inválido para {codigo}")
                        continue

                    cursos = Curso.objects.filter(grado=grado, curso=curso)
                    if not cursos.exists():
                        errores += 1
                        errores_detalle.append(f"Grado {grado}, Curso {curso} no existe para {codigo}")
                        continue

                    nombre_curso = cursos.first().nombre

                    Estudiante.objects.create(
                        codigo=codigo,
                        nombre=nombre,
                        apellido=apellido,
                        curso=nombre_curso
                    )

                    _crear_usuario_estudiante(codigo, "1234")
                    exitosos += 1

                except Exception as e:
                    errores += 1
                    errores_detalle.append(f"Error en fila: {str(e)}")

            mensaje = f"Importados: {exitosos}, Errores: {errores}"
            if errores > 0:
                messages.warning(request, mensaje)
                for detalle in errores_detalle[:5]:
                    messages.warning(request, f"  • {detalle}")
            else:
                messages.success(request, mensaje)

            return redirect("estudiantes")

        except Exception as e:
            messages.error(request, f"Error al procesar archivo: {str(e)}")
            return redirect("estudiantes")

    return render(request, "core/importar_estudiantes.html")


@login_required(login_url="login")
def editar_estudiante(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)

    if request.method == "POST":
        curso = get_object_or_404(Curso, id=request.POST["curso"])
        estudiante.codigo = request.POST["codigo"]
        estudiante.nombre = request.POST["nombre"]
        estudiante.apellido = request.POST["apellido"]
        estudiante.curso = curso.nombre
        estudiante.save()
        if request.user.is_superuser:
            return redirect("estudiantes")
        return redirect("estudiantes_por_curso", curso.id)

    cursos = Curso.objects.all()
    return render(request, "core/editar_estudiante.html", {
        "estudiante": estudiante,
        "cursos": cursos
    })


@requiere_coordinador
def eliminar_estudiante(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    estudiante.delete()
    return redirect("estudiantes")


@requiere_coordinador
def docentes(request):
    lista = Docente.objects.all()
    return render(request, "core/docentes.html", {"docentes": lista})


@requiere_coordinador
def agregar_docente(request):
    if request.method == "POST":
        Docente.objects.create(
            codigo=request.POST["codigo"],
            nombre=request.POST["nombre"],
            apellido=request.POST["apellido"],
            materia=request.POST["materia"]
        )
        return redirect("docentes")

    return render(request, "core/agregar_docente.html")


@requiere_coordinador
def editar_docente(request, id):
    docente = get_object_or_404(Docente, id=id)

    if request.method == "POST":
        docente.codigo = request.POST["codigo"]
        docente.nombre = request.POST["nombre"]
        docente.apellido = request.POST["apellido"]
        docente.materia = request.POST["materia"]
        docente.save()
        return redirect("docentes")

    return render(request, "core/editar_docente.html", {"docente": docente})


@requiere_coordinador
def eliminar_docente(request, id):
    docente = get_object_or_404(Docente, id=id)
    docente.delete()
    return redirect("docentes")


@requiere_coordinador
def faltas(request):
    lista = Falta.objects.select_related('estudiante', 'docente').order_by('-fecha')
    return render(request, "core/faltas.html", {"faltas": lista})


@login_required(login_url="login")
@login_required(login_url="login")
def api_buscar_estudiantes(request):
    """API para buscar estudiantes por grado, curso y nombre"""
    from django.http import JsonResponse

    grado = request.GET.get('grado', '')
    curso = request.GET.get('curso', '')
    nombre = request.GET.get('nombre', '')

    queryset = Estudiante.objects.all()

    if grado:
        try:
            grado = int(grado)
            # Filtrar por cursos que coincidan con el grado
            cursos_ids = Curso.objects.filter(grado=grado).values_list('nombre', flat=True)
            queryset = queryset.filter(curso__in=cursos_ids)
        except ValueError:
            pass

    if curso:
        try:
            curso = int(curso)
            # Filtrar por curso específico
            cursos_ids = Curso.objects.filter(grado=int(grado) if grado else 0, curso=str(curso).zfill(2)).values_list('nombre', flat=True)
            queryset = queryset.filter(curso__in=cursos_ids)
        except (ValueError, TypeError):
            pass

    if nombre:
        # Buscar por nombre o código
        queryset = queryset.filter(
            nombre__icontains=nombre
        ) | queryset.filter(
            apellido__icontains=nombre
        ) | queryset.filter(
            codigo__icontains=nombre
        )

    estudiantes = list(queryset.values('id', 'codigo', 'nombre', 'apellido', 'curso')[:20])

    return JsonResponse({
        'estudiantes': estudiantes
    })


@login_required(login_url="login")
def api_cursos_por_grado(request):
    """API para obtener cursos por grado"""
    from django.http import JsonResponse

    grado = request.GET.get('grado', '')

    if grado:
        try:
            grado = int(grado)
            cursos = list(Curso.objects.filter(grado=grado).values('id', 'grado', 'curso', 'nombre'))
            return JsonResponse({'cursos': cursos})
        except ValueError:
            pass

    return JsonResponse({'cursos': []})


@login_required(login_url="login")
def agregar_falta(request):
    if request.method == "POST":
        tipo = request.POST["tipo"]

        Falta.objects.create(
            estudiante=get_object_or_404(Estudiante, id=request.POST["estudiante"]),
            docente=get_object_or_404(Docente, id=request.POST["docente"]),
            fecha=request.POST["fecha"],
            tipo=tipo,
            hora=request.POST.get("hora", ""),
            estado="Pendiente",
            motivo=""
        )
        messages.success(request, "Falta registrada correctamente.")
        if request.user.is_superuser:
            return redirect("faltas")
        return redirect("faltas_pendientes")

    grados = sorted(set(Curso.objects.values_list('grado', flat=True)))
    return render(request, "core/agregar_falta.html", {
        "grados": grados,
        "docentes": Docente.objects.all(),
        "cursos": Curso.objects.all()
    })


@requiere_coordinador
def editar_falta(request, id):
    falta = get_object_or_404(Falta, id=id)

    if request.method == "POST":
        tipo = request.POST["tipo"]

        falta.estudiante = get_object_or_404(Estudiante, id=request.POST["estudiante"])
        falta.docente = get_object_or_404(Docente, id=request.POST["docente"])
        falta.fecha = request.POST["fecha"]
        falta.tipo = tipo
        falta.hora = request.POST.get("hora", "")
        falta.motivo = request.POST.get("motivo", "")
        falta.estado = request.POST["estado"]
        falta.save()
        return redirect("faltas")

    return render(request, "core/editar_falta.html", {
        "falta": falta,
        "estudiantes": Estudiante.objects.all(),
        "docentes": Docente.objects.all()
    })


@requiere_coordinador
def eliminar_falta(request, id):
    falta = get_object_or_404(Falta, id=id)
    falta.delete()
    return redirect("faltas")


@login_required(login_url="login")
def faltas_pendientes(request):
    pendientes = Falta.objects.filter(estado="Pendiente").select_related(
        'estudiante', 'docente'
    ).order_by("-fecha")
    return render(request, "core/faltas_pendientes.html", {"pendientes": pendientes})


@login_required(login_url="login")
def revisar_falta(request, id):
    falta = get_object_or_404(Falta, id=id)

    if request.method == "POST":
        if not request.user.is_superuser:
            return acceso_denegado(request, "Solo el coordinador puede aprobar o rechazar una falta.")
        accion = request.POST["accion"]
        if accion == "aprobar":
            falta.estado = "Aprobada"
        elif accion == "rechazar":
            falta.estado = "Rechazada"
        falta.save()
        messages.success(request, "Falta actualizada correctamente.")
        return redirect("faltas_pendientes")

    return render(request, "core/revisar_falta.html", {"falta": falta})


@login_required(login_url="login")
def mi_historial(request):
    estudiante = Estudiante.objects.filter(nombre__iexact=request.user.username).first()
    if not estudiante:
        estudiante = Estudiante.objects.filter(apellido__iexact=request.user.username).first()
    if not estudiante:
        estudiante = Estudiante.objects.filter(codigo__iexact=request.user.username).first()
    if not estudiante:
        messages.warning(request, "No hay registro de estudiante asociado a tu usuario.")
        return render(request, "core/historial_estudiante.html", {
            "estudiante": None,
            "faltas": [],
            "origen": "dashboard"
        })

    faltas = Falta.objects.filter(estudiante=estudiante).select_related('docente').order_by("-fecha")
    return render(request, "core/historial_estudiante.html", {
        "estudiante": estudiante,
        "faltas": faltas,
        "origen": "dashboard"
    })


@login_required(login_url="login")
def historial_estudiante(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    faltas = Falta.objects.filter(estudiante=estudiante).select_related('docente').order_by("-fecha")
    origen = request.GET.get("origen", "estudiantes" if request.user.is_superuser else "dashboard")
    curso_id = request.GET.get("curso", "")

    return render(request, "core/historial_estudiante.html", {
        "estudiante": estudiante,
        "faltas": faltas,
        "origen": origen,
        "curso_id": curso_id
    })


@requiere_coordinador
def estadisticas(request):
    cursos = Curso.objects.all()
    return render(request, "core/estadisticas.html", {"cursos": cursos})


@login_required(login_url="login")
def estadisticas_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    estudiantes_curso = Estudiante.objects.filter(curso=curso.nombre)
    faltas_curso = Falta.objects.filter(estudiante__curso=curso.nombre)

    total_faltas = faltas_curso.count()
    pendientes = faltas_curso.filter(estado="Pendiente").count()
    aprobadas = faltas_curso.filter(estado="Aprobada").count()
    rechazadas = faltas_curso.filter(estado="Rechazada").count()

    estudiante_mas_faltas = (
        estudiantes_curso.annotate(total=Count("falta"))
        .order_by("-total")
        .first()
    )

    # Estadisticas adicionales
    estudiantes_sin_faltas = estudiantes_curso.annotate(total_faltas=Count("falta")).filter(total_faltas=0).count()

    # Top 3 estudiantes con mas faltas
    top_estudiantes = (
        estudiantes_curso.annotate(total=Count("falta"))
        .order_by("-total")[:3]
    )

    # Distribucion por tipo de falta (con porcentaje calculado)
    faltas_por_tipo = []
    for tipo, label in Falta.TIPO_FALTA:
        count = faltas_curso.filter(tipo=tipo).count()
        porcentaje = (count / total_faltas * 100) if total_faltas > 0 else 0
        faltas_por_tipo.append({"tipo": label, "count": count, "porcentaje": round(porcentaje, 1)})

    # Distribucion por docente
    from django.db.models import Count as DjangoCount
    faltas_por_docente = (
        faltas_curso.values('docente__nombre', 'docente__apellido')
        .annotate(count=DjangoCount('id'))
        .order_by('-count')[:5]
    )

    # Promedio de faltas por estudiante
    promedio_faltas = total_faltas / estudiantes_curso.count() if estudiantes_curso.count() > 0 else 0

    # Tasa de aprobacion
    tasa_aprobacion = (aprobadas / total_faltas * 100) if total_faltas > 0 else 0

    return render(request, "core/estadisticas_curso.html", {
        "curso": curso,
        "total_faltas": total_faltas,
        "pendientes": pendientes,
        "aprobadas": aprobadas,
        "rechazadas": rechazadas,
        "estudiante_mas_faltas": estudiante_mas_faltas,
        "estudiantes_count": estudiantes_curso.count(),
        "estudiantes_sin_faltas": estudiantes_sin_faltas,
        "top_estudiantes": top_estudiantes,
        "faltas_por_tipo": faltas_por_tipo,
        "faltas_por_docente": faltas_por_docente,
        "promedio_faltas": round(promedio_faltas, 2),
        "tasa_aprobacion": round(tasa_aprobacion, 1),
    })


@login_required(login_url="login")
def justificar_falta(request, id):
    falta = get_object_or_404(Falta, id=id)

    if request.method == "POST":
        if "documento" not in request.FILES:
            messages.error(request, "Debes adjuntar un documento (por ejemplo, la excusa firmada por el acudiente) para justificar la falta.")
            return render(request, "core/justificar_falta.html", {"falta": falta})

        falta.fecha_justificacion = request.POST["fecha_justificacion"]
        falta.observaciones = request.POST["observaciones"]
        falta.justificada = True
        falta.documento = request.FILES["documento"]

        falta.save()
        messages.success(request, "Justificación enviada correctamente.")
        return redirect("historial_estudiante", falta.estudiante.id)

    return render(request, "core/justificar_falta.html", {"falta": falta})


@login_required(login_url="login")
def cambiar_contrasena_propia(request):
    """Cambiar propia contraseña - disponible para coordinador y estudiantes"""
    if request.method == "POST":
        contrasena_actual = request.POST.get("contrasena_actual", "").strip()
        contrasena_nueva = request.POST.get("contrasena_nueva", "").strip()
        contrasena_confirma = request.POST.get("contrasena_confirma", "").strip()

        usuario = request.user

        if not usuario.check_password(contrasena_actual):
            messages.error(request, "La contraseña actual es incorrecta.")
            return render(request, "core/cambiar_contrasena_propia.html")

        if not contrasena_nueva:
            messages.error(request, "La nueva contraseña no puede estar vacía.")
            return render(request, "core/cambiar_contrasena_propia.html")

        if contrasena_nueva != contrasena_confirma:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "core/cambiar_contrasena_propia.html")

        if contrasena_nueva == contrasena_actual:
            messages.error(request, "La nueva contraseña debe ser diferente a la actual.")
            return render(request, "core/cambiar_contrasena_propia.html")

        if len(contrasena_nueva) < 4:
            messages.error(request, "La contraseña debe tener al menos 4 caracteres.")
            return render(request, "core/cambiar_contrasena_propia.html")

        usuario.set_password(contrasena_nueva)
        usuario.save()

        messages.success(request, "Contraseña cambiada exitosamente.")
        return redirect("dashboard")

    return render(request, "core/cambiar_contrasena_propia.html")


@requiere_coordinador
def cambiar_contrasena_estudiante(request, id):
    """Coordinador cambia contraseña de un estudiante"""
    estudiante = get_object_or_404(Estudiante, id=id)
    usuario = get_object_or_404(User, username=estudiante.codigo)

    if request.method == "POST":
        contrasena_nueva = request.POST.get("contrasena_nueva", "").strip()
        contrasena_confirma = request.POST.get("contrasena_confirma", "").strip()

        if not contrasena_nueva:
            messages.error(request, "La contraseña no puede estar vacía.")
            return render(request, "core/cambiar_contrasena_estudiante.html", {"estudiante": estudiante})

        if contrasena_nueva != contrasena_confirma:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "core/cambiar_contrasena_estudiante.html", {"estudiante": estudiante})

        if len(contrasena_nueva) < 4:
            messages.error(request, "La contraseña debe tener al menos 4 caracteres.")
            return render(request, "core/cambiar_contrasena_estudiante.html", {"estudiante": estudiante})

        usuario.set_password(contrasena_nueva)
        usuario.save()

        messages.success(request, f"Contraseña de {estudiante.nombre} {estudiante.apellido} cambiada exitosamente.")
        return redirect("estudiantes")

    return render(request, "core/cambiar_contrasena_estudiante.html", {"estudiante": estudiante})


def olvide_contrasena(request):
    if request.method == "POST":
        usuario_texto = request.POST.get("usuario", "").strip()
        if usuario_texto:
            SolicitudContrasena.objects.create(usuario_texto=usuario_texto)
        messages.success(
            request,
            "Tu solicitud fue enviada. El coordinador se pondrá en contacto contigo para restablecer tu contraseña."
        )
        return redirect("olvide_contrasena")

    return render(request, "core/olvide_contrasena.html")


@requiere_coordinador
def solicitudes_contrasena(request):
    solicitudes = SolicitudContrasena.objects.filter(atendida=False)
    for s in solicitudes:
        s.estudiante_rel = Estudiante.objects.filter(codigo=s.usuario_texto).first()
        s.usuario_rel = User.objects.filter(username=s.usuario_texto).first()
    return render(request, "core/solicitudes_contrasena.html", {"solicitudes": solicitudes})


@requiere_coordinador
def marcar_solicitud_atendida(request, id):
    solicitud = get_object_or_404(SolicitudContrasena, id=id)
    solicitud.atendida = True
    solicitud.save()
    messages.success(request, "Solicitud marcada como atendida.")
    return redirect("solicitudes_contrasena")


@requiere_coordinador
def restablecer_contrasena_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    solicitud_id = request.GET.get("solicitud") or request.POST.get("solicitud")

    if request.method == "POST":
        contrasena_nueva = request.POST.get("contrasena_nueva", "").strip()
        contrasena_confirma = request.POST.get("contrasena_confirma", "").strip()

        if not contrasena_nueva:
            messages.error(request, "La contraseña no puede estar vacía.")
            return render(request, "core/restablecer_contrasena_usuario.html", {"usuario": usuario, "solicitud_id": solicitud_id})

        if contrasena_nueva != contrasena_confirma:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "core/restablecer_contrasena_usuario.html", {"usuario": usuario, "solicitud_id": solicitud_id})

        if len(contrasena_nueva) < 4:
            messages.error(request, "La contraseña debe tener al menos 4 caracteres.")
            return render(request, "core/restablecer_contrasena_usuario.html", {"usuario": usuario, "solicitud_id": solicitud_id})

        usuario.set_password(contrasena_nueva)
        usuario.save()

        if solicitud_id:
            SolicitudContrasena.objects.filter(id=solicitud_id).update(atendida=True)

        messages.success(request, f"Contraseña de {usuario.username} restablecida correctamente.")
        return redirect("solicitudes_contrasena")

    return render(request, "core/restablecer_contrasena_usuario.html", {"usuario": usuario, "solicitud_id": solicitud_id})
