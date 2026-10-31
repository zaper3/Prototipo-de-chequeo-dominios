# Guía reutilizable de README para proyectos Z3

Una estructura de presentación para futuros repositorios, aplicada aquí sin cambiar el producto. Es un archivo del repositorio, **no una skill instalada ni una actualización automática de otros proyectos**.

## Principios

1. **Primero el producto.** Portada propia, promesa breve y enlaces de entrada. La estética no debe esconder el estado de validación.
2. **Un vistazo antes de instalar.** Dos o tres capturas relevantes, legibles y con alt text. Distinguir captura real, fixture, render y mockup; nunca presentar una imagen ilustrativa como evidencia.
3. **Capacidades y límites juntos.** Qué hace, qué no hace y qué está pendiente. Separar implementado, probado y aprobado.
4. **Empezar sin adivinar.** Requisitos, comandos reproducibles, directorio de ejecución, puertos y primera acción.
5. **Un documento, dos idiomas.** `README.md` en español; `README.en.md` en inglés. Misma información material y mismos comandos; enlaces recíprocos y advertencia si la UI solo tiene un idioma.
6. **Datos y confianza.** Explicar dónde se guarda la información, retención, secretos, backups y límites de seguridad.
7. **Evolución visible.** Documentación, desarrollo, calidad, SemVer y evidencias; no declarar una nueva release por rediseñar el README.
8. **Sin suposiciones legales.** No copiar licencia, badges o promesas de otro proyecto. Confirmar qué archivos y releases existen.

## Secciones y equivalencias

| Español | English | Contenido mínimo |
|---|---|---|
| Portada + resumen | Cover + summary | Nombre, propósito, stack, versión real y navegación. |
| Un vistazo | At a glance | Capturas con procedencia, fecha y límites. |
| Qué puedes hacer | What you can do | Tabla de capacidades verificadas. |
| Empezar | Get started | Requisitos, instalación, ejecución y primera acción. |
| Perfiles / modos | Profiles / modes | Alcance y diferencias si existen. |
| Cómo interpretar el resultado | Understanding the result | Explicar indicadores, estados y límites. |
| Datos y configuración | Data and configuration | Persistencia, opciones, integraciones y recuperación. |
| Seguridad y límites | Security and limitations | Riesgos, uso permitido y capacidades pendientes. |
| Documentación | Documentation | Mapa de documentos enlazados, no texto duplicado. |
| Desarrollo y verificación | Development and verification | Stack, comandos, CI y gates no realizados. |
| Licencia / atribuciones | License / attribution | Solo términos realmente definidos por el proyecto. |

Una sección específica de dominio (como riesgo OSINT o control SSH) debe sustituirse por el concepto propio del nuevo producto. No se copian endpoints, paths locales, proveedores, números de tests, vulnerabilidades o datos de objetivos entre repositorios.

## Esqueleto para copiar

Sustituye los marcadores y comprueba los enlaces; las secciones opcionales se eliminan solo si no aplican.

```markdown
<div align="center">

![Portada del proyecto](docs/media/cover.svg)

# NOMBRE DEL PROYECTO

**Una frase concreta sobre el valor que aporta.**

STACK · PLATAFORMAS · MODELO DE USO

[Empezar](#empezar) · [Documentación](#documentación) · [English](README.en.md)

</div>

---

**VERSIÓN — estado real.** Qué es, para quién y qué se ha verificado.

> Advertencia de uso, privacidad o prerelease si corresponde.

## Un vistazo

![Vista principal y descripción accesible](docs/media/main.png)

*Tipo de imagen, procedencia, fecha y datos reales/sintéticos.*

## Qué puedes hacer

| Función | Comportamiento y límites |
|---|---|
| Capacidad | Implementación verificada; limitaciones explícitas. |

## Empezar

Requisitos, comandos desde la raíz y primera acción comprobada.

## Perfiles y resultados

Opcional: modos, indicadores y cómo leerlos.

## Datos y configuración

Dónde se guardan; retención; secretos; backup y restauración.

## Seguridad y límites

Riesgos conocidos y funciones fuera de alcance.

## Documentación

Mapa de documentos y enlaces existentes.

## Desarrollo y verificación

Stack, comandos reproducibles, CI y gates pendientes.

---

Autoría y licencia realmente establecida; no inferir una licencia.
```

## Checklist de publicación

- README principal en español y traducción inglesa equivalentes.
- Estado de versión y release confirmado; badges enlazan a jobs reales.
- Capturas sin secretos, información privada, rutas personales o historial del operador.
- Alt text y pies comprensibles; renders/fixtures identificados explícitamente.
- Comandos, defaults, endpoints y límites contrastados con código/configuración.
- Enlaces, anchors y recursos comprobados; paridad de comandos ES/EN.
- No se cambia licencia, visibilidad, tag, release ni lógica de producto sin autorización.
- Revisión visual, CI y escaneos/pruebas con terceros distinguidos; usar `NOT_RUN` cuando corresponda.

En este proyecto, `node scripts/check-docs.mjs` comprueba el conjunto documental y `node scripts/docs/check-readme.mjs` añade anchors, paridad y procedencia de medios.
