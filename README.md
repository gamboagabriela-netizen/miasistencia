# 📋 GUÍA RÁPIDA DE VALIDACIÓN

**Tiempo total**: 10-15 minutos  
**Dificultad**: Muy fácil (solo clickear)

---

## ✋ ANTES DE EMPEZAR

### Verificar que el servidor está corriendo:

**Terminal** (PowerShell):

```powershell
cd control_fallas (donde esté la ruta)
python manage.py runserver
```

**Deberías ver**:

```
Starting development server at http://127.0.0.1:8000/
```

Si no ves esto → El servidor no está corriendo. Intenta de nuevo.

---

## 🌐 PASO 0: Abrir Navegador

Abre: `http://localhost:8000`

Deberías ver: Página de LOGIN

---

## 🔑 PASO 1: LOGIN (30 segundos)

**Ingresa estos datos exactamente:**

- Usuario: `coordinador`
- Contraseña: `1234`
- Tipo Usuario: `Coordinador`

Click: **LOGIN**

**Esperado**: Entras al dashboard

Si falla: "Credenciales inválidas" → Verifica los datos exactos

---



## ✅ VALIDAR LAS 8 CORRECCIONES



### CORRECCIÓN #1: Estructura Grado + Curso

**Tiempo**: 1 minuto

**Pasos**:

1. Click en **CURSOS** (menú izquierda)
2. Mira la tabla

**¿Qué ves?**

- ✓ Columnas: Grado | Curso | Nombre
- ✓ Datos: Grado 10, Curso 01, Nombre 10A
- ✓ NO hay columna "Sección"

**Si ves esto**: ✅ FUNCIONA

---



### CORRECCIÓN #2: Importar CSV

**Tiempo**: 3 minutos

**Pasos**:

1. Click en **ESTUDIANTES** (menú)
2. **¿Ves estos 3 botones?**
  ```
   [Agregar Estudiante (Nuevo)]  [Importar Estudiantes]  [Descargar Plantilla]
  ```
3. Click en **DESCARGAR PLANTILLA**
4. Se descarga archivo `estudiantes.csv`
5. Abre con Notepad
6. **¿Ves este encabezado?**
  ```
   codigo,nombre,apellido,grado,curso
  ```
7. Añade estas líneas (copia y pega):
  ```
   2026501,Juan,Prueba,10,01
   2026502,María,Prueba,10,01
   2026503,Carlos,Prueba,10,02
  ```
8. Guarda: `Ctrl+S`
9. Vuelve a navegador
10. Click en **IMPORTAR ESTUDIANTES**
11. Click en **"Elegir archivo"** → Selecciona el CSV editado
12. Click en **IMPORTAR**

**Esperado**: 

- ✓ Mensaje de éxito
- ✓ Los 3 nuevos estudiantes aparecen en la lista

**Si ves esto**: ✅ FUNCIONA

---



### CORRECCIÓN #3: Búsqueda Dinámica en Faltas

**Tiempo**: 2 minutos

**Pasos**:

1. Click en **FALTAS** (menú)
2. Click en **AGREGAR FALTA**
3. **¿Ves estos campos?**
  - Grado (dropdown)
  - Curso (dropdown - vacío al inicio)
  - Estudiante (búsqueda)
4. Selecciona: **Grado 10**
5. **¿Se llena automáticamente el campo Curso?**
  - ✓ SÍ → Debería mostrar: 01, 02, 03, etc.
6. Selecciona: **Curso 01**
7. En campo **Estudiante**, escribe: `Juan`
8. **¿Aparecen sugerencias debajo?**
  - ✓ SÍ → "Juan Prueba" aparece como opción
9. Click en la sugerencia

**Esperado**:

- ✓ Curso se carga sin recargar página
- ✓ Sugerencias aparecen mientras escribes
- ✓ Puedes seleccionar estudiante

**Si ves esto**: ✅ FUNCIONA

---



### CORRECCIÓN #4: Campo Motivo Condicional

**Tiempo**: 1 minuto

**Pasos**:

1. Mismo formulario de FALTAS
2. Busca campo: **TIPO DE FALTA**
3. Selecciona: **"Día Completo"**
4. **¿Ves campos "Hora desde" y "Hora hasta"?**
  - ✓ NO → Correcto
5. Selecciona: **"Parcial"**
6. **¿Ahora SÍ ves campos "Hora desde", "Hora hasta", "Motivo"?**
  - ✓ SÍ → Correcto

**Esperado**:

- ✓ Día Completo → Sin campos hora
- ✓ Parcial → Con campos hora

**Si ves esto**: ✅ FUNCIONA

---



### CORRECCIÓN #5: Usuario = Código

**Tiempo**: 1 minuto

**Pasos**:

1. Top derecha → Click en **tu nombre** → **LOGOUT**
2. Página de LOGIN
3. Ingresa:
  - Usuario: `2026501` (código del estudiante que importaste)
  - Contraseña: `1234`
  - Tipo: **ESTUDIANTE**
4. Click: **LOGIN**

**Esperado**:

- ✓ Loguearse con el código funciona
- ✓ Ves página del estudiante

**Si ves esto**: ✅ FUNCIONA

---



### CORRECCIÓN #6: Cambiar Contraseña Coordinador

**Tiempo**: 1 minuto

**Pasos**:

1. **LOGOUT** (eres estudiante ahora)
2. Login como coordinador nuevamente: `coordinador` / `1234`
3. Top derecha → Click en **tu nombre** → **CAMBIAR CONTRASEÑA**
  OR: Ve directo a: `http://localhost:8000/cambiar-contrasena/`
4. **¿Ves este formulario?**
  ```
   Contraseña Actual: ______
   Nueva Contraseña: ______
   Confirmar Nueva: ______
  ```
5. Ingresa:
  - Actual: `1234`
  - Nueva: `nueva123`
  - Confirmar: `nueva123`
6. Click: **CAMBIAR CONTRASEÑA**

**Esperado**:

- ✓ Mensaje de éxito
- ✓ Sin errores

1. **LOGOUT**
2. Login con nueva contraseña:
  - Usuario: `coordinador`
  - Contraseña: `nueva123`

**Si loguearse funciona**: ✅ FUNCIONA

---



### CORRECCIÓN #7: Cambiar Contraseña Estudiante

**Tiempo**: 1 minuto

**Pasos**:

1. Login como coordinador (coordinador / nueva123)
2. Click en **ESTUDIANTES**
3. Busca: "Juan Prueba" (estudiante que importaste)
4. Click sobre el nombre del estudiante
5. **¿Ves botón "CAMBIAR CONTRASEÑA"?**
  - ✓ SÍ → Click en él
6. **¿Ves este formulario?** (SIN pedir contraseña actual)
  ```
   Nueva Contraseña: ______
   Confirmar Nueva: ______
  ```
7. Ingresa:
  - Nueva: `pass456`
  - Confirmar: `pass456`
8. Click: **CAMBIAR CONTRASEÑA**

**Esperado**:

- ✓ Mensaje de éxito
- ✓ Sin pedir contraseña actual

**Si ves esto**: ✅ FUNCIONA

---



### CORRECCIÓN #8: Interfaz de Registro Simplificada

**Tiempo**: 30 segundos

**Pasos**:

1. Click en **ESTUDIANTES** (menú)
2. **¿Ves estos 3 botones arriba de la tabla?**
  ```
   [Agregar Estudiante (Nuevo)]  [Importar Estudiantes]  [Descargar Plantilla]
  ```

**Esperado**:

- ✓ Los 3 botones están visibles
- ✓ Están separados y claros

**Si ves esto**: ✅ FUNCIONA

---



## 📊 RESULTADO FINAL

Copia esto y marca:

```
□ Corrección 1: Estructura Grado+Curso .................... ✅
□ Corrección 2: Importación CSV ........................... ✅
□ Corrección 3: Búsqueda en Faltas ........................ ✅
□ Corrección 4: Campo Motivo Condicional ................. ✅
□ Corrección 5: Usuario = Código .......................... ✅
□ Corrección 6: Cambiar Contraseña Coordinador ........... ✅
□ Corrección 7: Cambiar Contraseña Estudiante ............ ✅
□ Corrección 8: Interfaz de Registro Simplificada ........ ✅
```

