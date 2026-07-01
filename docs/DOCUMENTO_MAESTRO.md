# DOCUMENTO MAESTRO — Proyecto Comunica2

| | |
|---|---|
| **Proyecto** | Comunica2 — Plataforma web de comunicación escolar digital |
| **Institución** | Instituto Superior Politécnico Córdoba (ISPC) |
| **Carrera** | Tecnicatura Superior en Desarrollo Web y Aplicaciones Digitales |
| **Espacio curricular** | Proyecto Integrador II — 2026 (Anual) |
| **Docente** | Alejandro Vicente SANTANGELO |
| **Autor** | Maximiliano Fernández — desarrollo individual, dos roles declarados |
| **Cuentas GitHub** | `lanusroots` (Desarrollador A) · `fernandezmaxar` (Desarrollador B) — ambas del autor |
| **Repositorio** | https://github.com/comunica2-ispc-2026/comunica2 |

> Este es el documento maestro del proyecto: la fuente única de verdad de la documentación
> formal. Vive en el repositorio (`docs/`), evoluciona junto con el desarrollo y se exporta a
> PDF en cada entrega de evidencia. Su historial de cambios en Git es parte de la evidencia del
> proceso.

## Registro de versiones del documento

| Fecha | Versión | Cambios | Autor |
|-------|---------|---------|-------|
| 26/04/2026 | 1.0 | Entrega Evidencia 1: situación, solución, requerimientos, backlog, actas | Equipo |
| 30/06/2026 | 1.1 | Incorporación de Historias de Usuario (Parte II, sección 6) | lanusroots |
| 30/06/2026 | 1.2 | Nota metodológica: desarrollo individual transparente | lanusroots |
| 30/06/2026 | 1.3 | Proceso de trabajo ágil: Git Flow, DoR, DoD, Story Points, Code Review | lanusroots |
| 01/07/2026 | 1.4 | Nota metodológica revisada: dos roles de desarrollo declarados, ambas cuentas aportan código | lanusroots |

## Nota metodológica

Este proyecto es desarrollado por una sola persona (Maximiliano Fernández), que opera **dos
roles de desarrollo** de forma declarada, mediante dos cuentas de GitHub, con el fin de
reproducir de manera completa el flujo de trabajo de una *software factory*:

- **`lanusroots`** — Desarrollador A: implementación de funcionalidades y revisión de código.
- **`fernandezmaxar`** — Desarrollador B: implementación de funcionalidades y revisión de código.

Ambas cuentas aportan código en ramas paralelas (`feature/HU-XX`) y se revisan mutuamente
mediante *Pull Requests*. La configuración de ramas protegidas exige la aprobación de la cuenta
opuesta antes de cada *merge* (GitHub no permite aprobar el propio PR), lo que garantiza que el
ciclo de *code review* se ejecute de forma efectiva y no meramente formal.

De este modo, el historial del repositorio refleja un proceso colaborativo real —commits de dos
autores, PRs cruzados y revisiones documentadas— sin recurrir a la invención de integrantes. La
doble autoría se declara explícitamente en este documento para preservar la transparencia del
trabajo.

Las ceremonias de equipo (dailies, *sprint reviews*, retrospectivas y actas) se documentan
reflejando esta modalidad de desarrollo individual con dos roles. La Parte I de este documento
conserva el contenido de la Evidencia 1 tal como fue elaborada en la fase de arranque del proyecto.

## Proceso de trabajo ágil

### Flujo de ramas (Git Flow)

| Rama | Propósito |
|------|-----------|
| `main` | Código estable y entregable. Solo recibe *merges* al cerrar un sprint o una versión. Protegida. |
| `develop` | Rama de integración. Reúne las funcionalidades terminadas. Protegida. |
| `feature/HU-XX-descripcion` | Una rama por Historia de Usuario, creada desde `develop`. |
| `release/vX.Y` | Preparación de una entrega/versión (ajustes finales, sin nuevas funcionalidades). |
| `hotfix/descripcion` | Corrección urgente sobre `main` ya entregado. |

**Convención de commits:** `feat` (funcionalidad), `fix` (corrección), `refactor` (reorganización), `docs` (documentación), `chore` (tareas técnicas). Formato: `tipo(HU-XX): descripción`.

**Integración:** ninguna rama protegida (`main`, `develop`) se modifica con *push* directo. Todo cambio pasa por *Pull Request* con revisión aprobada por la cuenta revisora.

### Definition of Ready (DoR) — cuándo una HU puede entrar a un sprint

Una Historia de Usuario está *lista* para ser comprometida cuando:

- Tiene descripción en formato "Como… quiero… para…".
- Tiene criterios de aceptación en formato DADO / CUANDO / ENTONCES.
- Está estimada en *Story Points*.
- Tiene identificadas sus dependencias (p. ej., requiere el modelo de datos previo).
- Está cargada como *Issue* en GitHub, con su *label*, *milestone* y responsable asignado.

### Definition of Done (DoD) — cuándo una HU está terminada

Una Historia de Usuario está *terminada* cuando:

- El código implementa y satisface **todos** sus criterios de aceptación.
- Sigue las convenciones del stack (PEP 8 en Python/Django; guía de estilo de Angular).
- Se integró mediante *Pull Request* hacia `develop`.
- Tuvo *code review* aprobado según el checklist de calidad (por la cuenta revisora).
- No rompe la compilación ni las pruebas (cuando exista integración continua).
- Está documentado lo necesario (docstrings/comentarios; endpoints en Swagger si aplica).
- El *Issue* quedó cerrado y la tarjeta movida a *Done* en el tablero.
- La rama *feature* fue borrada tras el *merge*.

### Estimación con Story Points

Se usa la sucesión de Fibonacci como escala de complejidad relativa:

| Puntos | Interpretación |
|--------|----------------|
| 1 | Trivial (cambio mínimo, sin incertidumbre). |
| 2–3 | Sencilla, bien acotada. |
| 5 | Complejidad media. |
| 8 | Compleja; conviene revisar si puede dividirse. |
| 13 | Muy compleja; **debe** dividirse en historias menores. |

### Checklist de Code Review

Toda revisión de *Pull Request* sigue las seis dimensiones de calidad. El detalle operativo vive
en la plantilla de *Pull Request* del repositorio (`.github/pull_request_template.md`):

1. **Legibilidad** — código claro, nombres descriptivos.
2. **Seguridad** — sin credenciales expuestas, entradas validadas, acceso por rol respetado.
3. **Pruebas** — probado localmente; pruebas pasan cuando aplican.
4. **Arquitectura** — respeta la separación de capas (modelo / API / cliente).
5. **Convenciones** — sigue el estilo del stack y la convención de commits.
6. **Documentación** — lo necesario para entender y mantener el código.

---

# PARTE I · Definición del Proyecto
*Corresponde a la Evidencia 1 — entregada el 26/04/2026.*

## 1. Situación problemática

**¿Quiénes tienen el problema?**
Las familias (padres, madres y tutores), los docentes y las autoridades de escuelas primarias de gestión público-privada en Argentina. En una institución de entre 100 y 300 alumnos, esto representa centenares de intercambios semanales entre la escuela y los hogares.

**¿En qué contexto ocurre?**
Cada vez que la institución necesita comunicar algo a una familia —un aviso, una citación, una autorización, una observación de conducta— o cada vez que una familia necesita comunicarse con la escuela, el único canal formal disponible es la libreta de comunicaciones en papel. Este cuadernillo lo transporta el propio alumno, todos los días, entre el aula y su hogar.

**¿Cuál es el problema concreto?**
El modelo depende completamente de que un niño no pierda, moje, rompa u olvide su cuadernillo. No existe ningún mecanismo alternativo. Cuando la libreta no llega, la comunicación no ocurre. Además, la única forma de confirmar que un mensaje fue leído es la firma del familiar —que puede ser omitida o falsificada sin consecuencias inmediatas visibles para la institución.

**¿Qué consecuencias tiene?**
- Las familias no reciben avisos a tiempo cuando el cuadernillo no llega a casa.
- Los docentes no pueden verificar si un comunicado fue efectivamente leído.
- Las autoridades no tienen un registro centralizado ni historial propio de las comunicaciones emitidas.
- Una libreta extraviada borra el historial completo del alumno durante todo el año lectivo.
- No existe canal formal para que la familia inicie una consulta fuera del horario escolar.

**¿Por qué una solución digital puede ayudar?**
Una aplicación web permitiría que los mensajes lleguen directamente al dispositivo de cada familiar, sin depender del alumno como intermediario físico. Reemplazaría la firma en papel por un acuse de lectura digital con fecha y hora, garantizando trazabilidad real. Además, centralizaría en un solo sistema el historial de comunicados, calificaciones e inasistencias, accesible para cada actor según su rol, desde cualquier lugar y en cualquier momento.

**Proceso de detección (Pain Points).** El problema se eligió por consenso del equipo tras una dinámica de detección de Pain Points en la que se relevaron 13 problemas reales agrupados en salud, educación, comercio local y trámites. Se seleccionó la gestión de comunicaciones escolares en papel, identificada a partir de la experiencia real de un integrante como padre de una alumna de nivel primario.

## 2. Solución propuesta

**Nombre del sistema:** Comunica2 — Plataforma web de comunicación escolar digital.

**¿Qué hace?**
Comunica2 es una aplicación web que reemplaza la libreta de comunicaciones en papel por un sistema digital centralizado. Permite que docentes, autoridades y familias intercambien mensajes de forma directa, ordenada y verificable, sin que el alumno tenga que transportar ningún documento físico.

**¿Para quién es?** Tres tipos de usuarios:
- **Las familias** — reciben los comunicados en su cuenta personal, confirman la lectura con un acuse digital y pueden enviar mensajes a docentes o autoridades cuando lo necesiten.
- **Los docentes** — redactan y envían comunicados a familias individuales o a toda una sección, registran calificaciones e inasistencias, y pueden ver quién leyó cada mensaje.
- **Las autoridades (directivos y secretaría)** — emiten circulares institucionales para toda la escuela, gestionan los datos del establecimiento y tienen una vista completa de la actividad comunicacional.

**¿Qué valor aporta?**
- Las familias reciben los avisos en el momento, sin depender de que el alumno entregue el cuadernillo.
- La institución tiene por primera vez un registro propio, centralizado e histórico de todas las comunicaciones.
- Los docentes pueden verificar qué familias leyeron cada mensaje y cuándo.
- Se elimina la posibilidad de falsificación de firmas, uno de los problemas más frecuentes del modelo en papel.

**¿Qué queda fuera del alcance?**
El sistema no reemplaza un sistema de gestión escolar completo. No incluye liquidación de haberes docentes, gestión contable, planificaciones curriculares ni integración con sistemas provinciales de registro educativo. Su foco exclusivo es la comunicación entre la institución y las familias, que es exactamente lo que hoy cubre la libreta en papel.

## 3. Listado de requerimientos

### Requerimientos Funcionales

| ID | Requerimiento |
|----|---------------|
| RF01 | Registro e inicio de sesión de usuarios con roles diferenciados: administrador, autoridad, docente y familia. |
| RF02 | Cada usuario puede actualizar su perfil y cambiar su contraseña. |
| RF03 | El administrador puede crear, editar y dar de baja usuarios. |
| RF04 | El acceso a cada sección se restringe según el rol del usuario autenticado. |
| RF05 | Registrar alumnos con sus datos: nombre, apellido, DNI, sección, turno, domicilio y contactos. |
| RF06 | Vincular cada alumno a uno o más familiares o tutores. |
| RF07 | El administrador puede asignar alumnos a secciones y turnos. |
| RF08 | Docentes y autoridades pueden redactar y enviar comunicados a una familia, a una sección o a toda la escuela. |
| RF09 | Las familias reciben los comunicados en su bandeja y confirman la lectura con un acuse digital. |
| RF10 | El sistema registra la fecha y hora del acuse de lectura de cada familiar. |
| RF11 | Las familias pueden enviar mensajes dirigidos al docente o a las autoridades. |
| RF12 | Cada comunicado se almacena en el historial del alumno correspondiente. |
| RF13 | Los docentes pueden registrar calificaciones por alumno, área curricular y fecha. |
| RF14 | Las familias pueden consultar las calificaciones de su hijo/a. |
| RF15 | Las autoridades pueden acceder a las calificaciones de todos los alumnos. |
| RF16 | Los docentes pueden registrar inasistencias y llegadas tarde por alumno y fecha. |
| RF17 | Las familias pueden consultar el registro de asistencia de su hijo/a. |
| RF18 | Las familias pueden justificar una inasistencia desde la plataforma. |
| RF19 | El sistema mantiene un historial completo de comunicados, calificaciones e inasistencias por alumno durante todo el ciclo lectivo. |
| RF20 | Cada actor accede al historial según su rol. |

### Requerimientos No Funcionales

| ID | Tipo | Requerimiento |
|----|------|---------------|
| RNF01 | Usabilidad | Interfaz clara e intuitiva para usuarios sin conocimientos técnicos (las familias son el perfil menos técnico). |
| RNF02 | Responsividad | Funciona correctamente en móviles, tablets y computadoras de escritorio. |
| RNF03 | Seguridad | Las contraseñas se almacenan de forma segura (no en texto plano). El acceso a la API se protege con autenticación por token. |
| RNF04 | Disponibilidad | Disponible en horario escolar extendido (7:00–20:00 hs) con inactividad planificada mínima. |
| RNF05 | Rendimiento | Las operaciones principales (envío y lectura de comunicados) responden en menos de 3 segundos en condiciones normales. |
| RNF06 | Trazabilidad | Toda acción relevante queda registrada con usuario y timestamp. |
| RNF07 | Mantenibilidad | Código organizado según las convenciones del stack y documentado para futuras modificaciones. |

## 4. Backlog inicial

**Prioridad Alta — sin esto el sistema no funciona**

| ID | Tipo | Ítem |
|----|------|------|
| BK01 | Técnico | Configurar repositorio Git con estructura de ramas |
| BK02 | Técnico | Configurar proyecto backend (Django) |
| BK03 | Técnico | Configurar proyecto frontend (Angular) |
| BK04 | Técnico | Diseñar e implementar base de datos relacional |
| BK05 | Funcional | Registro e inicio de sesión de usuarios |
| BK06 | Funcional | Gestión de roles (familia, docente, autoridad, admin) |
| BK07 | Funcional | Registro de alumnos y vinculación con familias |
| BK08 | Funcional | Envío de comunicados (individual y grupal) |
| BK09 | Funcional | Recepción y acuse de lectura de comunicados |

**Prioridad Media — importante pero puede esperar una o dos semanas**

| ID | Tipo | Ítem |
|----|------|------|
| BK10 | Funcional | Registro de calificaciones por área curricular |
| BK11 | Funcional | Consulta de calificaciones por parte de la familia |
| BK12 | Funcional | Registro de inasistencias y llegadas tarde |
| BK13 | Funcional | Justificación de inasistencias por parte de la familia |
| BK14 | Funcional | Historial de comunicados por alumno |
| BK15 | Funcional | Vista de estado de lectura por docente/autoridad |
| BK16 | Técnico | Configurar autenticación con token |
| BK17 | Técnico | Primer deploy en entorno de prueba |

**Prioridad Baja — deseable pero no crítico**

| ID | Tipo | Ítem |
|----|------|------|
| BK18 | Funcional | Panel de administración general (alta/baja de usuarios) |
| BK19 | Funcional | Emisión de circulares institucionales masivas |
| BK20 | Funcional | Gestión de secciones y turnos escolares |
| BK21 | Técnico | Pruebas funcionales e integración del sistema completo |
| BK22 | Técnico | Deploy en entorno de producción (Railway, Render u otro) |
| BK23 | Documentación | Documentar endpoints de la API (Swagger o Postman) |
| BK24 | Documentación | Completar README del repositorio |
| BK25 | Documentación | Redactar informe final del ABP |

**Tablero ágil:** [insertar link de GitHub Projects] — *(ver sección Tablero Kanban)*

## 5. Actas de reunión

### Acta N° 1 — Martes 17/03/2026 · 19:00–20:00 hs · Google Meet
**Participantes:** Maximiliano Fernández (Moderador), Compañero 1 (Secretario), Compañero 2 (Timekeeper), Compañero 3 (Participante).
**Temas:** presentación del espacio curricular y lectura del plan anual; presentación de integrantes; organización del equipo (canal de comunicación y herramienta de documentación); lectura de la consigna de la Evidencia 1.
**Decisiones:** encuentros sincrónicos los martes 19:00 hs por Google Meet; Google Drive para documentos y WhatsApp para comunicación informal; próxima reunión enfocada en dinámica de Pain Points; nombre provisorio del equipo: Comunica2.
**Tareas:** leer el plan completo (Todos, 20/03); preparar 3 problemas para Pain Points (Todos, 24/03); crear carpeta compartida en Drive (Compañero 1, 19/03).

### Acta N° 2 — Martes 24/03/2026 · 19:00–20:15 hs · Google Meet
**Participantes:** Compañero 1 (Moderador), Compañero 2 (Secretario), Compañero 3 (Timekeeper), Maximiliano Fernández (Participante).
**Temas:** revisión de tareas; dinámica de Pain Points (13 problemas relevados en salud, educación, comercio local y trámites); evaluación de viabilidad; elección del problema por consenso.
**Decisiones:** se elige la gestión de comunicaciones escolares en papel; se descarta una app de turnos médicos por ser un problema ya muy abordado; nombre definido: Comunica2; se acuerda Trello como tablero ágil y GitHub para el repositorio.
**Tareas:** redactar la situación problemática (Maximiliano, 28/03); crear tablero en Trello (Compañero 3, 26/03); crear repositorio en GitHub con estructura de ramas (Compañero 2, 26/03); investigar soluciones similares (Compañero 1, 28/03).

### Acta N° 3 — Martes 31/03/2026 · 19:00–20:30 hs · Google Meet
**Participantes:** Compañero 2 (Moderador), Compañero 3 (Secretario), Maximiliano Fernández (Timekeeper), Compañero 1 (Participante).
**Temas:** revisión de tareas; revisión grupal de la situación problemática; definición de la solución propuesta; discusión del alcance; primeros requerimientos funcionales.
**Decisiones:** se aprueba la situación problemática con ajustes menores; foco exclusivo en comunicación institución-familia; se identifican 4 módulos (autenticación y roles, comunicados, calificaciones, inasistencias); se valida viabilidad con la docente.
**Tareas:** redactar la solución propuesta (Compañero 1, 04/04); listar RF (Maximiliano, 04/04); listar RNF (Compañero 2, 04/04); primeros ítems al tablero (Compañero 3, 04/04).

### Acta N° 4 — Martes 07/04/2026 · 19:00–20:30 hs · Google Meet
**Participantes:** Compañero 3 (Moderador), Maximiliano Fernández (Secretario), Compañero 1 (Timekeeper), Compañero 2 (Participante).
**Temas:** revisión de tareas; ajuste grupal del listado de requerimientos; armado y priorización del backlog en Trello; configuración del repositorio (ramas main, develop, feature); distribución de tareas.
**Decisiones:** se aprueban 20 RF y 7 RNF; backlog en tres columnas (Pendiente, En progreso, Hecho); 9 ítems Alta, 9 Media, 7 Baja; BK01 y BK24 movidos a En progreso.
**Tareas:** ordenar el backlog en Trello (Compañero 3, 10/04); captura del tablero (Compañero 2, 10/04); iniciar el documento final (Maximiliano, 12/04); revisar ortografía y coherencia (Compañero 1, 14/04).

### Acta N° 5 — Martes 14/04/2026 · 19:00–20:00 hs · Google Meet
**Participantes:** Maximiliano Fernández (Moderador), Compañero 1 (Timekeeper), Compañero 2 (Secretario), Compañero 3 (Participante).
**Temas:** lectura completa del documento final; revisión de coherencia entre secciones; verificación del backlog; correcciones finales; definición del nombre del PDF y responsable de la exportación.
**Decisiones:** se aprueba el documento final; se ajusta la redacción de tres RF; se verifica acceso público al tablero; Maximiliano exporta el PDF y lo sube a Moodle.
**Tareas:** exportar a PDF (Maximiliano, 20/04); verificar acceso al tablero (Compañero 3, 16/04); subir el PDF a Moodle (Maximiliano, 26/04).

---

# PARTE II · Diseño

## 6. Historias de Usuario y criterios de aceptación

Los 20 requerimientos funcionales se consolidan en 14 Historias de Usuario, organizadas por
módulo. Cada una mantiene la trazabilidad con los RF que cubre y define sus criterios de
aceptación en formato DADO / CUANDO / ENTONCES.

### Índice

| HU | Título | Módulo | RF | Prioridad |
|----|--------|--------|----|-----------|
| HU-01 | Inicio de sesión con control de acceso por rol | Autenticación | RF01, RF04 | Alta |
| HU-02 | Gestión del perfil y contraseña | Autenticación | RF02 | Media |
| HU-03 | Administración de usuarios (ABM) | Autenticación | RF03 | Baja |
| HU-04 | Registro y gestión de alumnos | Alumnos | RF05 | Alta |
| HU-05 | Vinculación de alumnos con sus familias | Alumnos | RF06 | Alta |
| HU-06 | Organización en secciones y turnos | Alumnos | RF07 | Baja |
| HU-07 | Envío de comunicados | Comunicados | RF08 | Alta |
| HU-08 | Recepción y acuse de lectura | Comunicados | RF09, RF10 | Alta |
| HU-09 | Mensajes de la familia hacia la escuela | Comunicados | RF11 | Media |
| HU-10 | Registro de calificaciones | Calificaciones | RF13 | Media |
| HU-11 | Consulta de calificaciones | Calificaciones | RF14, RF15 | Media |
| HU-12 | Registro de asistencia | Inasistencias | RF16 | Media |
| HU-13 | Consulta y justificación de inasistencias | Inasistencias | RF17, RF18 | Media |
| HU-14 | Historial integral del alumno | Historial | RF12, RF19, RF20 | Media |

### Módulo A — Autenticación y usuarios

#### HU-01 — Inicio de sesión con control de acceso por rol · RF01, RF04 · Alta
**Como** usuario registrado (familia, docente, autoridad o administrador) **quiero** iniciar sesión con mis credenciales y acceder solo a lo que me corresponde **para** usar la plataforma de forma segura según mi función.
- **CA-01 Inicio exitoso:** DADO que soy usuario registrado, CUANDO ingreso email y contraseña correctos, ENTONCES el sistema me autentica, me entrega un token y me redirige al panel de mi rol.
- **CA-02 Credenciales inválidas:** DADO que soy usuario, CUANDO ingreso datos incorrectos, ENTONCES muestra "Credenciales incorrectas" y no inicia sesión.
- **CA-03 Acceso por rol:** DADO que inicié sesión con un rol, CUANDO intento entrar a una sección ajena a mi rol, ENTONCES el sistema deniega el acceso.
- **CA-04 Sesión requerida:** DADO que no inicié sesión, CUANDO intento abrir una página protegida, ENTONCES me redirige al inicio de sesión.

#### HU-02 — Gestión del perfil y contraseña · RF02 · Media
**Como** usuario autenticado **quiero** actualizar mis datos y cambiar mi contraseña **para** mantener mi información al día y mi cuenta segura.
- **CA-01 Actualizar perfil:** DADO que estoy en mi perfil, CUANDO modifico datos permitidos y guardo, ENTONCES el sistema persiste los cambios y confirma.
- **CA-02 Cambiar contraseña:** DADO que estoy en seguridad, CUANDO ingreso mi contraseña actual y una nueva válida (mín. 8 caracteres), ENTONCES la actualiza.
- **CA-03 Contraseña actual incorrecta:** DADO que cambio mi contraseña, CUANDO ingreso mal la actual, ENTONCES muestra el error y no cambia nada.

#### HU-03 — Administración de usuarios (ABM) · RF03 · Baja
**Como** administrador **quiero** crear, editar y dar de baja usuarios **para** mantener actualizado el padrón de accesos.
- **CA-01 Crear:** DADO que soy admin, CUANDO completo datos de un nuevo usuario y confirmo, ENTONCES se crea la cuenta.
- **CA-02 Editar:** DADO que existe un usuario, CUANDO modifico sus datos o rol, ENTONCES se actualiza.
- **CA-03 Baja:** DADO que existe un usuario activo, CUANDO lo doy de baja, ENTONCES pierde acceso pero su historial se conserva.
- **CA-04 Email duplicado:** DADO que creo un usuario, CUANDO el email ya existe, ENTONCES muestra el error y no lo crea.

### Módulo B — Alumnos y vínculos

#### HU-04 — Registro y gestión de alumnos · RF05 · Alta
**Como** administrador o autoridad **quiero** registrar y mantener los datos de los alumnos **para** asociarles comunicados, calificaciones e inasistencias.
- **CA-01 Registrar:** DADO que soy admin/autoridad, CUANDO completo los datos del alumno, ENTONCES queda registrado y disponible.
- **CA-02 DNI único:** DADO que registro un alumno, CUANDO el DNI ya existe, ENTONCES muestra el error y no lo registra.
- **CA-03 Editar:** DADO que existe un alumno, CUANDO modifico sus datos, ENTONCES se actualiza.
- **CA-04 Campos obligatorios:** DADO que registro un alumno, CUANDO faltan campos obligatorios, ENTONCES muestra aviso y no guarda.

#### HU-05 — Vinculación de alumnos con sus familias · RF06 · Alta
**Como** administrador o autoridad **quiero** vincular cada alumno con uno o más familiares **para** que la información llegue a las personas correctas.
- **CA-01 Vincular:** DADO un alumno y un usuario familia, CUANDO los vinculo, ENTONCES ese familiar ve la info del alumno y recibe sus comunicados.
- **CA-02 Varios familiares:** DADO un alumno con un familiar, CUANDO vinculo un segundo, ENTONCES ambos quedan asociados.
- **CA-03 Familiar con varios hijos:** DADO un familiar con varios hijos, CUANDO está vinculado a varios alumnos, ENTONCES ve cada uno por separado.
- **CA-04 Desvincular:** DADO un vínculo existente, CUANDO lo elimino, ENTONCES el familiar deja de acceder a esa info.

#### HU-06 — Organización en secciones y turnos · RF07 · Baja
**Como** administrador **quiero** asignar alumnos a secciones y turnos **para** dirigir comunicados grupales y organizar la información por curso.
- **CA-01 Asignar:** DADO un alumno registrado, CUANDO lo asigno a sección y turno, ENTONCES queda incluido en ese grupo.
- **CA-02 Reasignar:** DADO un alumno en una sección, CUANDO lo muevo, ENTONCES se actualiza manteniendo su historial.
- **CA-03 Listar:** DADO alumnos asignados, CUANDO consulto una sección, ENTONCES veo su listado de integrantes.

### Módulo C — Comunicados

#### HU-07 — Envío de comunicados · RF08 · Alta
**Como** docente o autoridad **quiero** enviar comunicados a una familia, una sección o toda la escuela **para** informar de forma directa y verificable.
- **CA-01 Individual:** DADO que soy docente/autoridad, CUANDO elijo una familia como destinatario, ENTONCES se envía solo a ella y queda registrado.
- **CA-02 Por sección:** DADO que elijo una sección, ENTONCES se envía a todas las familias de esa sección.
- **CA-03 Circular institucional:** DADO que soy autoridad, CUANDO elijo toda la escuela, ENTONCES se envía a todas las familias.
- **CA-04 Incompleto:** DADO que redacto un comunicado, CUANDO falta título, cuerpo o destinatario, ENTONCES muestra aviso y no lo envía.

#### HU-08 — Recepción y acuse de lectura · RF09, RF10 · Alta
**Como** familiar **quiero** recibir los comunicados y confirmar que los leí **para** estar al tanto sin depender del cuaderno.
- **CA-01 Recibir:** DADO un comunicado dirigido a mí, CUANDO entro a mi bandeja, ENTONCES lo veo con título, remitente y fecha, marcado "no leído".
- **CA-02 Confirmar lectura:** DADO un comunicado sin leer, CUANDO confirmo lectura, ENTONCES registra mi acuse con fecha y hora y pasa a "leído".
- **CA-03 Acuse visible:** DADO que confirmé, CUANDO el emisor consulta, ENTONCES ve mi nombre con fecha y hora.
- **CA-04 Pendientes:** DADO un comunicado a varias familias, CUANDO el emisor consulta el estado, ENTONCES distingue leídos de pendientes.

#### HU-09 — Mensajes de la familia hacia la escuela · RF11 · Media
**Como** familiar **quiero** enviar mensajes al docente o a las autoridades **para** consultar sin depender del horario escolar.
- **CA-01 Enviar:** DADO que soy familiar, CUANDO redacto y elijo destinatario, ENTONCES se envía y queda registrado.
- **CA-02 Recepción:** DADO que envié, CUANDO el destinatario entra a su bandeja, ENTONCES ve el mensaje con remitente, alumno y fecha.
- **CA-03 Vacío:** DADO que envío un mensaje, CUANDO el cuerpo está vacío, ENTONCES no se envía.

### Módulo D — Calificaciones

#### HU-10 — Registro de calificaciones · RF13 · Media
**Como** docente **quiero** registrar calificaciones por alumno, área y fecha **para** seguir el rendimiento.
- **CA-01 Cargar:** DADO que soy docente, CUANDO registro una calificación con área y fecha, ENTONCES se guarda en el historial del alumno.
- **CA-02 Editar:** DADO una calificación cargada, CUANDO la modifico, ENTONCES se actualiza conservando la fecha.
- **CA-03 Validar valor:** DADO que cargo una calificación, CUANDO el valor está fuera de rango, ENTONCES muestra aviso y no guarda.

#### HU-11 — Consulta de calificaciones · RF14, RF15 · Media
**Como** familiar (de mi hijo/a) o autoridad (de todos) **quiero** consultar las calificaciones **para** seguir el rendimiento académico.
- **CA-01 Familia:** DADO que soy familiar, CUANDO entro a calificaciones, ENTONCES veo solo las de mi hijo/a.
- **CA-02 Autoridad:** DADO que soy autoridad, ENTONCES puedo consultar las de todos los alumnos.
- **CA-03 Aislamiento:** DADO que soy familiar, CUANDO intento ver un alumno sin vínculo, ENTONCES se deniega el acceso.

### Módulo E — Inasistencias

#### HU-12 — Registro de asistencia · RF16 · Media
**Como** docente **quiero** registrar inasistencias y llegadas tarde por alumno y fecha **para** controlar la asistencia.
- **CA-01 Inasistencia:** DADO que soy docente, CUANDO registro una inasistencia, ENTONCES se guarda en el historial.
- **CA-02 Llegada tarde:** DADO que soy docente, CUANDO registro una tardanza, ENTONCES se guarda diferenciada de la inasistencia.
- **CA-03 Sin duplicar:** DADO una inasistencia ya registrada, CUANDO intento repetirla, ENTONCES lo advierte y no duplica.

#### HU-13 — Consulta y justificación de inasistencias · RF17, RF18 · Media
**Como** familiar **quiero** consultar y justificar las inasistencias de mi hijo/a **para** seguir su asistencia y dejar constancia.
- **CA-01 Consultar:** DADO que soy familiar, CUANDO entro a asistencia, ENTONCES veo inasistencias y tardanzas con fechas.
- **CA-02 Justificar:** DADO una inasistencia sin justificar, CUANDO la justifico con motivo, ENTONCES queda "justificada".
- **CA-03 Visible para la escuela:** DADO que justifiqué, CUANDO el docente/autoridad consulta, ENTONCES ve motivo y estado.

### Módulo F — Historial

#### HU-14 — Historial integral del alumno · RF12, RF19, RF20 · Media
**Como** actor del sistema **quiero** acceder al historial completo de un alumno según mi rol **para** consultar todo el ciclo en un solo lugar.
- **CA-01 Consolidado:** DADO un alumno con actividad, CUANDO accedo a su historial, ENTONCES veo por fecha sus comunicados, calificaciones e inasistencias.
- **CA-02 Comunicados archivados:** DADO un comunicado asociado, CUANDO consulto el historial, ENTONCES aparece con su estado de lectura.
- **CA-03 Acceso por rol:** DADO mi rol, CUANDO accedo, ENTONCES veo solo lo que me autoriza.
- **CA-04 Persistencia:** DADO que avanza el ciclo, CUANDO consulto, ENTONCES la información se conserva completa todo el ciclo.

> **Nota sobre los RNF:** los requerimientos no funcionales no se traducen en HU; se aplican de
> forma transversal y se verifican como criterios de calidad del sistema. El acuse con fecha/hora
> (HU-08) materializa el RNF06; el control de acceso por rol (HU-01) y la autenticación por token
> materializan el RNF03.

## 7. Arquitectura del sistema
*(Pendiente — Sprint 1.)* Diagrama de arquitectura cliente-servidor en capas: Angular (cliente) → API REST (Django REST Framework) → PostgreSQL. Se incluirá el diagrama de servicios y la justificación de las decisiones de arquitectura.

## 8. Modelo de datos
*(Pendiente — Sprint 1.)* Diagrama entidad-relación (DER), descripción de entidades y relaciones, y notas de normalización. Base del esquema relacional en PostgreSQL.

---

# PARTE III · Construcción — Backend
*(Pendiente — Sprints 1 y 2. Cubre Evidencias 2 y 3.)*

## 9. API REST
Endpoints por módulo, autenticación por token, manejo de errores y validaciones.

## 10. Documentación de la API
Documentación de endpoints con Swagger / Postman.

---

# PARTE IV · Frontend e integración
*(Pendiente — segundo cuatrimestre. Cubre Evidencias 4 y 5.)*

---

# PARTE V · Testing, despliegue y cierre
*(Pendiente. Cubre Evidencia 6 y la defensa oral.)*
