<!--
  Plantilla de Pull Request — Proyecto Comunica2
  Implementa el checklist de Code Review y la Definition of Done del proyecto.
  Completá las secciones y marcá las casillas antes de solicitar la revisión.
-->

## Historia de Usuario relacionada

Closes #<!-- número del Issue de la HU, p. ej. Closes #5 -->

## Descripción del cambio

<!-- Qué resuelve este PR y cómo. Breve. -->

## Criterios de aceptación cumplidos

<!-- Copiá los CA de la HU y marcá los que cumple este PR -->
- [ ] CA-01:
- [ ] CA-02:
- [ ] CA-03:

---

## Checklist de Code Review

> El revisor verifica estas seis dimensiones antes de aprobar.

**Legibilidad**
- [ ] El código es claro y los nombres (variables, funciones, clases) son descriptivos.

**Seguridad**
- [ ] No expone credenciales ni secretos (nada fuera de `.env`).
- [ ] Valida las entradas y respeta el control de acceso por rol.

**Pruebas**
- [ ] Probado localmente; los criterios de aceptación funcionan.
- [ ] Las pruebas automáticas pasan (cuando aplican).

**Arquitectura**
- [ ] Respeta la separación de capas (modelo de datos / API / cliente).
- [ ] No duplica lógica ni introduce acoplamientos innecesarios.

**Convenciones**
- [ ] Sigue el estilo del stack (PEP 8 / guía de Angular).
- [ ] Los commits siguen la convención `tipo(HU-XX): descripción`.

**Documentación**
- [ ] Documentado lo necesario (docstrings/comentarios; endpoints en Swagger si aplica).

---

## Definition of Done

- [ ] Cumple **todos** los criterios de aceptación de la HU.
- [ ] Revisado y aprobado por la cuenta revisora.
- [ ] No rompe la compilación ni las pruebas.
- [ ] Listo para *merge* a `develop`; la rama *feature* se borrará tras el *merge*.
