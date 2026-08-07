"""
El resolver de alcance -- el corazon de la fase 2.

Reduce CUALQUIER sub-rol a una moneda unica: un queryset concreto de Secciones
(o de Alumnos). Con eso, toda pregunta de permiso ("puede emitir a este
destino?", "puede leer a este alumno?") se vuelve un test de pertenencia contra
ese set, en vez de un `has_object_permission` lleno de ramas por rol.

Es la misma jugada que el fan-out on write de comunicados: en vez de resolver la
complejidad en cada consulta, la colapsas a algo concreto y despues preguntar es
trivial.

Autoridad = UNION de dos fuentes de alcance (7a):
- nivel/turno (AlcanceAutoridad): director/vice/preceptor.
- grupos (AlcanceGrupo): tesorero -> secciones de sus Grupos Personalizados.
Un mismo usuario podria tener ambas; la union lo cubre sin casos especiales.

Nota de diseno: la FAMILIA es el caso especial. Su alcance NO es la seccion de
sus hijos (no ve a los companeros): es el set de sus alumnos vinculados.
"""

from django.contrib.auth import get_user_model
from django.db.models import Q

from alumnos.models import Alumno, Seccion

Rol = get_user_model().Rol


def _alcance_autoridad(user):
    """Secciones activas de una AUTORIDAD, unificando nivel/turno + grupos.
    Vacio si no tiene ninguna de las dos fuentes (ej. tesorero sin grupos)."""
    # Eje nivel/turno (director/vice/preceptor).
    filtro_nivel = Q()
    for fila in user.alcances.all():
        cond = Q(nivel=fila.nivel)
        if fila.turno:
            cond &= Q(turno=fila.turno)
        filtro_nivel |= cond

    tiene_grupos = user.alcances_grupo.exists()
    if not filtro_nivel and not tiene_grupos:
        return Seccion.objects.none()

    # Eje grupos (tesorero): secciones de los grupos donde el user tiene alcance.
    filtro_grupo = Q(grupos__alcances__autoridad=user)

    condicion = (filtro_nivel | filtro_grupo) if filtro_nivel else filtro_grupo
    return Seccion.objects.filter(condicion, activa=True).distinct()


def secciones_en_alcance(user):
    """Set concreto de Secciones sobre las que el usuario tiene alcance."""
    if user.rol == Rol.ADMINISTRADOR:
        return Seccion.objects.filter(activa=True)

    if user.rol == Rol.DOCENTE:
        return Seccion.objects.filter(
            docentes_asignados__docente=user,
            docentes_asignados__activa=True,
            activa=True,
        ).distinct()

    if user.rol == Rol.AUTORIDAD:
        return _alcance_autoridad(user)

    return Seccion.objects.none()  # FAMILIA: su eje son sus hijos, no la seccion


def alumnos_en_alcance(user):
    """Set concreto de Alumnos. La familia es el caso especial: su alcance son
    sus vinculos activos (sus hijos), no la seccion de sus hijos."""
    if user.rol == Rol.FAMILIA:
        return Alumno.objects.filter(
            vinculos__usuario=user, vinculos__activo=True, activo=True,
        ).distinct()

    return Alumno.objects.filter(
        seccion__in=secciones_en_alcance(user), activo=True
    )

# =============================================================================
# Dirección inversa del resolver (RF11 — mensajería bidireccional, S11).
#
# La mensajería reusa el MISMO resolver, ahora de forma simétrica: una familia y
# un docente/autoridad pueden conversar sí y solo sí comparten standing sobre un
# alumno. `pueden_conversar` es la compuerta AUTORITATIVA (usa el resolver hacia
# adelante, igual que destino_en_alcance / alumno_en_alcance). `contrapartes_de_
# alumno` y `familiares_de_alumno` son el resolver AL REVÉS, y sirven solo para
# descubrimiento/UX (a quién puedo escribirle): NO son autoritativas — si alguna
# vez difirieran del gate, el peor caso es mostrar a alguien que después da 403.
# Esa asimetría (autorización = forward, discovery = reverse) viaja al oficial.
# =============================================================================


def pueden_conversar(familia, contraparte, alumno):
    """Compuerta de la mensajería (RF11). True si `familia` (rol FAMILIA) y
    `contraparte` (rol DOCENTE/AUTORIDAD) comparten standing sobre `alumno`: la
    familia está vinculada al alumno Y el alumno cae en el alcance de la
    contraparte. Reúsa el resolver hacia adelante -> jamás diverge del resto de
    la autorización. No depende de quién inició el hilo (es simétrica)."""
    if familia.rol != Rol.FAMILIA:
        return False
    if contraparte.rol not in (Rol.DOCENTE, Rol.AUTORIDAD):
        return False
    familia_ok = alumno.vinculos.filter(usuario=familia, activo=True).exists()
    if not familia_ok:
        return False
    return alumnos_en_alcance(contraparte).filter(pk=alumno.pk).exists()


def contrapartes_de_alumno(alumno):
    """Reverse del resolver: docentes/autoridades con standing sobre `alumno`,
    para que la FAMILIA elija a quién escribirle. Docentes asignados a la sección
    + autoridades cuyo nivel/turno o grupo la cubre. Un alumno sin sección solo
    lo alcanza el admin (ESCUELA) -> no hay contraparte de mensajería. Discovery
    only: la autorización real la hace pueden_conversar (forward)."""
    User = get_user_model()
    sec = alumno.seccion
    if sec is None:
        return User.objects.none()

    docentes = User.objects.filter(
        rol=Rol.DOCENTE,
        secciones_asignadas__seccion=sec,
        secciones_asignadas__activa=True,
    )
    # nivel/turno en la MISMA fila de alcance (turno NULL = nivel completo).
    aut_nivel = User.objects.filter(rol=Rol.AUTORIDAD).filter(
        Q(alcances__nivel=sec.nivel)
        & (Q(alcances__turno__isnull=True) | Q(alcances__turno=sec.turno))
    )
    aut_grupo = User.objects.filter(
        rol=Rol.AUTORIDAD,
        alcances_grupo__grupo__secciones=sec,
    )
    return (docentes | aut_nivel | aut_grupo).distinct()


def familiares_de_alumno(alumno):
    """Reverse para la otra dirección: los familiares vinculados activos del
    alumno, para que el STAFF elija a qué familia escribirle. Discovery only."""
    User = get_user_model()
    return User.objects.filter(
        vinculos__alumno=alumno, vinculos__activo=True
    ).distinct()
