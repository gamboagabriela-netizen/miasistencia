from django.db import models


class Curso(models.Model):
    grado = models.IntegerField()
    curso = models.CharField(max_length=5, default="01")
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['grado', 'curso']
        unique_together = ('grado', 'curso')

    def __str__(self):
        return f"Grado {self.grado} - Curso {self.curso}"


class Estudiante(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    curso = models.CharField(max_length=20)

    class Meta:
        ordering = ['curso', 'apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido} {self.nombre} ({self.curso})"

    def get_curso_object(self):
        try:
            return Curso.objects.get(nombre=self.curso)
        except Curso.DoesNotExist:
            return None


class Docente(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    materia = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.apellido} {self.nombre}"


class Falta(models.Model):
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE
    )

    # Se mantiene para no perder la información existente.
    # Más adelante podemos relacionarlo automáticamente
    # con el docente que inició sesión.
    docente = models.ForeignKey(
        Docente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    fecha = models.DateField()

    TIPO_FALTA = [
        ("hora", "Por hora"),
        ("dia", "Todo el día"),
        ("retirada", "Retirada"),
    ]

    tipo = models.CharField(
        max_length=15,
        choices=TIPO_FALTA
    )

    # Para las inasistencias por hora
    hora = models.CharField(
        max_length=20,
        blank=True
    )

    # Información específica de una retirada
    quien_retiro = models.CharField(
        max_length=150,
        blank=True
    )

    motivo_retiro = models.TextField(
        blank=True
    )

    hora_retiro = models.TimeField(
        null=True,
        blank=True
    )

    motivo = models.TextField(
        blank=True
    )

    justificada = models.BooleanField(
        default=False
    )

    ESTADOS = [
        ("Pendiente", "Pendiente"),
        ("Aprobada", "Aprobada"),
        ("Rechazada", "Rechazada"),
        ("Registrada", "Registrada"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )

    fecha_justificacion = models.DateField(
        null=True,
        blank=True
    )

    observaciones = models.TextField(
        blank=True
    )

    documento = models.FileField(
        upload_to="justificaciones/",
        null=True,
        blank=True
    )

    fecha_revision = models.DateField(
        null=True,
        blank=True
    )

    observaciones_coordinador = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.estudiante} - {self.fecha} - {self.get_tipo_display()}"


class SolicitudContrasena(models.Model):
    usuario_texto = models.CharField(max_length=150)
    fecha = models.DateTimeField(auto_now_add=True)
    atendida = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.usuario_texto} ({self.fecha:%Y-%m-%d %H:%M})"
