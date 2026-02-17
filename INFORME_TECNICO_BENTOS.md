# INFORME TÉCNICO: Sistema BENTOS — Gestión de Bitácoras Electrónicas de Pesca

**Empresa:** Pesquero Quintero S.A.  
**Proyecto:** Sistema BENTOS — Software de Gestión y Análisis de Bitácoras MSC  
**Fecha:** Febrero 2026  
**Versión:** 1.0  

---

## ÍNDICE

1. [Resumen](#1-resumen)  
2. [Introducción](#2-introducción)  
3. [Objetivo General y Objetivos Específicos](#3-objetivo-general-y-objetivos-específicos)  
   - 3.1 Objetivo General  
   - 3.2 Objetivos Específicos  
4. [Problema](#4-problema)  
5. [Antecedentes](#5-antecedentes)  
6. [Descripción de la Actividad](#6-descripción-de-la-actividad)  
   - 6.1 Arquitectura del Sistema  
   - 6.2 Tecnologías Utilizadas  
   - 6.3 Módulos del Sistema  
   - 6.4 Modelo de Datos  
   - 6.5 Funcionalidades Principales  
   - 6.6 Flujo de Trabajo  
7. [Conclusión](#7-conclusión)  
8. [Bibliografía](#8-bibliografía)  

---

## 1. Resumen

El presente informe describe el diseño, desarrollo e implementación del sistema **BENTOS**, un software de escritorio desarrollado en Python para la empresa Pesquero Quintero S.A. El sistema tiene como propósito principal automatizar la extracción, almacenamiento y análisis de datos provenientes de bitácoras electrónicas de pesca emitidas por el Servicio Nacional de Pesca y Acuicultura (Sernapesca) en formato PDF. BENTOS fue diseñado para facilitar el cumplimiento de los estándares de trazabilidad y sostenibilidad exigidos por la certificación Marine Stewardship Council (MSC), reemplazando procesos de transcripción manual que son propensos a errores y altamente demandantes en tiempo. El sistema integra un motor de extracción de datos desde archivos PDF, almacenamiento en la nube mediante Google Firebase Firestore, y herramientas de visualización que incluyen gráficos estadísticos, mapas de calor georeferenciados e indicadores de sostenibilidad ecosistémica.

---

## 2. Introducción

La industria pesquera chilena enfrenta desafíos crecientes en materia de sostenibilidad y trazabilidad de sus operaciones. La certificación MSC (Marine Stewardship Council) es un estándar internacional que reconoce prácticas pesqueras sustentables, siendo un requisito cada vez más demandado por los mercados internacionales. Para obtener y mantener esta certificación, las empresas pesqueras deben demostrar un control exhaustivo de sus operaciones, incluyendo datos detallados de captura, descarte, esfuerzo pesquero y composición de especies por lance de pesca.

Pesquero Quintero S.A. opera embarcaciones dedicadas a la pesca de arrastre de camarón nailon (*Heterocarpus reedi*) y langostino colorado (*Pleuroncodes monodon*) en la costa central de Chile. Actualmente, Sernapesca emite bitácoras electrónicas en formato PDF que contienen toda la información operacional de cada viaje de pesca. Sin embargo, la extracción y análisis de estos datos se realizaba de forma manual, lo que generaba retrasos, inconsistencias y dificultades para consolidar la información requerida por los auditores de la certificación MSC.

El sistema BENTOS fue desarrollado como una solución tecnológica integral para automatizar este flujo de trabajo, permitiendo que la información de las bitácoras sea procesada, almacenada en la nube y analizada de forma eficiente, precisa y centralizada.

---

## 3. Objetivo General y Objetivos Específicos

### 3.1 Objetivo General

Desarrollar e implementar un sistema de software de escritorio que automatice la extracción, almacenamiento y análisis de datos provenientes de bitácoras electrónicas de pesca de Sernapesca, con el fin de facilitar el cumplimiento de los requisitos de trazabilidad y sostenibilidad de la certificación MSC para Pesquero Quintero S.A.

### 3.2 Objetivos Específicos

1. **Diseñar e implementar un motor de extracción automática de datos (parser)** capaz de procesar archivos PDF de bitácoras electrónicas de Sernapesca, extrayendo información general del viaje, datos de captura total, detalle de cada lance de pesca (incluyendo especies retenidas, descartadas e incidentales), coordenadas geográficas y observaciones, manejando correctamente tablas que se extienden entre múltiples páginas del documento.

2. **Desarrollar un sistema de almacenamiento centralizado en la nube** utilizando Google Firebase Firestore, que permita la persistencia, consulta y gestión de los datos extraídos de las bitácoras, garantizando la integridad, disponibilidad y trazabilidad de la información para auditorías MSC con un horizonte de retención mínimo de tres años.

3. **Construir una interfaz gráfica de usuario intuitiva y profesional** que integre funcionalidades de carga de bitácoras (individual y masiva), búsqueda avanzada con filtros múltiples, visualización estadística mediante gráficos interactivos, generación de mapas de calor georeferenciados y cálculo de indicadores de sostenibilidad ecosistémica (ratio merluza/especie objetivo), facilitando la toma de decisiones basada en datos.

---

## 4. Problema

Pesquero Quintero S.A. requiere mantener la certificación MSC para sus operaciones de pesca de camarón nailon y langostino colorado. Esta certificación exige un control detallado y demostrable de las capturas realizadas en cada viaje de pesca, incluyendo la composición de especies por lance, las cantidades retenidas y descartadas, las ubicaciones geográficas de las faenas y los indicadores de impacto ecosistémico como el ratio de captura incidental de merluza respecto a las especies objetivo.

Antes de la implementación de BENTOS, el proceso de gestión de esta información presentaba las siguientes problemáticas:

- **Transcripción manual:** Los datos de las bitácoras PDF de Sernapesca eran transcritos manualmente a hojas de cálculo, lo que consumía un tiempo significativo (estimado en varias horas por viaje con múltiples lances) y era propenso a errores de digitación.

- **Fragmentación de la información:** Los datos de diferentes viajes se encontraban dispersos en múltiples archivos locales sin un sistema centralizado de consulta, lo que dificultaba las auditorías y el análisis histórico.

- **Ausencia de análisis automatizado:** No existía un mecanismo para calcular automáticamente indicadores de sostenibilidad como el ratio merluza/especie objetivo, ni para generar visualizaciones geográficas de las operaciones de pesca.

- **Complejidad del formato PDF:** Las bitácoras de Sernapesca presentan tablas con estructuras variables (entre 4 y 9 columnas), tablas que se cortan entre páginas, lances declarados sin capturas, y diversas convenciones de formato que hacen inviable una extracción manual rápida y precisa.

- **Riesgo de incumplimiento:** La acumulación de bitácoras sin procesar y la falta de un sistema de seguimiento generaban riesgo de no disponer de la información necesaria durante las auditorías de certificación.

---

## 5. Antecedentes

La certificación MSC fue creada en 1997 como un programa de ecoetiquetado para productos del mar provenientes de pesquerías sustentables. En Chile, diversas pesquerías han obtenido esta certificación, lo que les permite acceder a mercados internacionales con mayores exigencias ambientales (Marine Stewardship Council, 2023).

Sernapesca, como entidad reguladora, implementó las bitácoras electrónicas de pesca como parte del sistema de monitoreo y control de las actividades pesqueras nacionales. Estas bitácoras registran información operacional detallada de cada viaje de pesca, incluyendo datos del zarpe, datos de la embarcación, detalle de lances (coordenadas, horarios, profundidades, composición de captura) y observaciones relevantes (Servicio Nacional de Pesca y Acuicultura, 2020).

La pesquería de camarón nailon (*Heterocarpus reedi*) opera principalmente en la zona central de Chile, utilizando arte de pesca de arrastre. La gestión sustentable de esta pesquería requiere el monitoreo continuo de la captura incidental de merluza común (*Merluccius gayi*), especie considerada como depredador incidental y cuyo ratio respecto a las especies objetivo es un indicador clave de sostenibilidad ecosistémica para la certificación MSC (Subsecretaría de Pesca y Acuicultura, 2022).

Pesquero Quintero S.A. opera con una frecuencia aproximada de dos recaladas por semana, con viajes de cuatro días que pueden generar entre 4 y 20 lances por viaje. La certificación MSC tiene una duración de cinco años, durante los cuales la empresa debe demostrar trazabilidad completa de sus operaciones con un mínimo de tres años de retención de datos.

---

## 6. Descripción de la Actividad

### 6.1 Arquitectura del Sistema

BENTOS sigue una arquitectura de tres capas adaptada a una aplicación de escritorio con almacenamiento en la nube:

```
┌──────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                      │
│              Interfaz Gráfica (CustomTkinter)                │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│    │ Subir PDFs   │  │ Buscar/      │  │ Admin Panel  │     │
│    │ (Drag&Drop)  │  │ Analizar     │  │ (Gestión)    │     │
│    └──────────────┘  └──────────────┘  └──────────────┘     │
├──────────────────────────────────────────────────────────────┤
│                    CAPA DE LÓGICA                            │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │ PDF Parser   │ │ Convertidor  │ │ Clasificador       │   │
│  │ (pdfplumber) │ │ Coordenadas  │ │ Especies MSC       │   │
│  └──────────────┘ └──────────────┘ └────────────────────┘   │
├──────────────────────────────────────────────────────────────┤
│                    CAPA DE DATOS                             │
│              Google Firebase Firestore (Nube)                │
│         ┌─────────────────────────────────────┐             │
│         │  Colección: viajes                   │             │
│         │    └── Subcolección: lances           │             │
│         └─────────────────────────────────────┘             │
│                 Respaldo local (JSON)                        │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 Tecnologías Utilizadas

| Componente | Tecnología | Versión | Propósito |
|---|---|---|---|
| Lenguaje | Python | 3.13 | Lenguaje de programación principal |
| Interfaz Gráfica | CustomTkinter | 5.2.1 | Framework de GUI moderno con tema oscuro |
| Extracción PDF | pdfplumber | 0.11.0 | Extracción de tablas y texto de PDFs |
| Base de Datos | Firebase Admin SDK | 6.4.0 | Conexión con Google Firestore |
| Procesamiento | pandas / numpy | 2.2.0 / 1.26.3 | Manipulación y análisis de datos |
| Georeferenciación | pyproj | 3.6.1 | Conversión de coordenadas geográficas |
| Mapas | folium | - | Generación de mapas de calor interactivos |
| Validación | pydantic | 2.5.3 | Validación de estructuras de datos |
| Diálogos | CTkMessagebox | 2.5 | Mensajes y alertas personalizados |
| Calendario | tkcalendar | - | Selector de fechas para filtros |
| Drag & Drop | tkinterdnd2 | - | Soporte de arrastrar y soltar archivos |
| Imágenes | Pillow | 10.2.0 | Procesamiento de imágenes para la GUI |

### 6.3 Módulos del Sistema

El sistema está organizado en los siguientes módulos:

#### 6.3.1 Motor de Extracción PDF (`pdf_parser_v2.py` — 1.153 líneas)

El parser es el componente central del sistema. Implementa un enfoque de **máquina de estados secuencial por tablas** que recopila todas las tablas de todas las páginas del PDF en orden, luego las clasifica y procesa secuencialmente. Este diseño resuelve el problema crítico de tablas que se cortan entre páginas.

**Tipos de tablas procesadas:**
- **INFORMACIÓN GENERAL:** Datos del viaje (nave, capitán, armador, fechas, folio).
- **CAPTURA TOTAL:** Resumen de todas las especies capturadas en el viaje (puede extenderse a la página 2).
- **DETALLE DE LANCE:** Tablas con 4, 8 o 9 columnas que contienen la información operacional de cada lance.
- **Tablas de continuación de especies:** Tablas de 6 columnas con datos de especies que continúan desde la página anterior.
- **Tablas standalone de especies:** Tablas independientes con header ESPECIE para lances sin captura o con observaciones.

**Proceso de extracción:**
1. Recopilación de todas las tablas de todas las páginas.
2. Clasificación de cada tabla según su estructura y contenido.
3. Procesamiento secuencial manteniendo el estado del lance actual.
4. Extracción de coordenadas, fechas, especies y observaciones.
5. Validación de datos y construcción de la estructura final.

#### 6.3.2 Convertidor de Coordenadas (`coordinate_converter.py` — 112 líneas)

Convierte las coordenadas geográficas del formato DMS (grados, minutos, segundos) utilizado en las bitácoras de Sernapesca (ej: `33° 51.21588' S`) al formato decimal necesario para la visualización en mapas y almacenamiento en Firebase.

#### 6.3.3 Clasificador de Especies MSC (`especies_config.py` — 213 líneas)

Define la taxonomía de especies según los criterios de la certificación MSC:
- **Especies objetivo:** Camarón nailon (*Heterocarpus reedi*), Langostino colorado (*Pleuroncodes monodon*).
- **Depredador incidental:** Merluza común (*Merluccius gayi*) — indicador crítico de sostenibilidad.
- **Fauna acompañante:** Congrio negro, lenguado, granadero, jaibas, entre otros.
- **Especies sensibles:** Tollo negro raspa (tiburón), Raya volantín.

Incluye funciones para calcular el **ratio merluza/especie objetivo** y generar alertas de sostenibilidad ecosistémica según umbrales definidos (verde ≤10%, amarillo 10-20%, rojo >20%).

#### 6.3.4 Gestor de Firebase (`firebase_manager.py` — 368 líneas)

Administra la conexión y operaciones CRUD con Google Firebase Firestore:
- Almacenamiento de viajes y lances como documentos y subcolecciones.
- Consultas con filtros múltiples (nave, capitán, fechas, especies).
- Eliminación de viajes con sus lances asociados.
- Modo local de respaldo en caso de falta de conectividad.

#### 6.3.5 Interfaz Gráfica (`app.py` — ~4.800 líneas)

La interfaz principal del sistema, construida con CustomTkinter con tema oscuro profesional. Incluye:
- Pantalla de inicio animada (Splash Screen).
- Dos secciones principales: Subir Bitácoras y Buscar/Analizar datos.
- Panel de administración para gestión de bitácoras existentes.
- Sistema de notificaciones.

### 6.4 Modelo de Datos

La estructura de datos en Firebase Firestore sigue el siguiente esquema:

```
Firestore
└── viajes (colección)
    └── {id_viaje} (documento)
        ├── id_viaje: "SERNAPESCA-BE-XXXXX"
        ├── nave_nombre: "Nombre de la nave"
        ├── capitan: "Nombre del capitán"
        ├── armador: "Razón social del armador"
        ├── fecha_zarpe: timestamp
        ├── fecha_recalada: timestamp
        ├── puerto_zarpe: "Puerto de salida"
        ├── puerto_recalada: "Puerto de llegada"
        ├── num_lances_total: número
        ├── timestamp_subida: timestamp
        │
        └── lances (subcolección)
            └── lance_XXX (documento)
                ├── numero_lance: número (0 = CAPTURA TOTAL)
                ├── fecha_inicio: timestamp
                ├── fecha_fin: timestamp
                ├── latitud_inicio: decimal
                ├── longitud_inicio: decimal
                ├── latitud_fin: decimal
                ├── longitud_fin: decimal
                ├── arte_pesca: "Tipo de arte"
                ├── observaciones: "Texto libre"
                ├── es_captura_total: booleano
                │
                └── especies (array)
                    └── {especie}
                        ├── nombre: "Nombre de la especie"
                        ├── tipo_captura: "retenida" | "descartada"
                        ├── cantidad_ton: decimal
                        ├── cantidad_unidades: entero
                        └── tipo_especie: "objetivo" | "acompañante" | ...
```

### 6.5 Funcionalidades Principales

#### Carga de Bitácoras
- Selección individual o múltiple de archivos PDF (hasta 5 simultáneos).
- Soporte de arrastrar y soltar (drag & drop) archivos directamente a la interfaz.
- Vista previa detallada de cada bitácora antes de confirmar la subida, incluyendo la tabla de captura total con todas las especies.
- Barra de progreso durante el procesamiento.
- Validación automática de datos antes del almacenamiento.

#### Búsqueda y Análisis
- Filtros avanzados: embarcación, capitán, rango de fechas de zarpe, especie.
- Presets rápidos de búsqueda: últimos 7 días, mes actual, año actual.
- Visualización de resultados como tarjetas individuales o resumen consolidado.
- Paginación de resultados.

#### Visualización de Datos
- **Gráficos de barras:** Distribución de capturas por especie (retenidas vs. descartadas).
- **Gráficos de resumen total:** Estadísticas consolidadas de múltiples viajes.
- **Mapa de calor georeferenciado:** Visualización interactiva en navegador web con:
  - Heat maps separados para captura objetivo y descarte.
  - Marcadores con números de lance y popups informativos detallados.
  - Porcentajes de composición de captura por lance.
  - Indicación visual de lances sin capturas.
  - Leyenda profesional y controles de capa.
  - Mini-mapa de navegación y modo pantalla completa.

#### Indicadores de Sostenibilidad
- Cálculo automático del ratio merluza/especie objetivo por lance y por viaje.
- Sistema de alertas por semáforo: verde (≤10%), amarillo (10-20%), rojo (>20%).
- Identificación de especies sensibles (tiburones, rayas).

#### Administración
- Panel de administración para visualizar y eliminar bitácoras del sistema.
- Sistema de notificaciones de operaciones realizadas.

### 6.6 Flujo de Trabajo

1. El capitán de la embarcación recibe la bitácora electrónica de Sernapesca en formato PDF al finalizar el viaje de pesca.
2. El usuario abre el sistema BENTOS y selecciona uno o varios archivos PDF para subir.
3. El sistema analiza automáticamente los PDFs, extrayendo toda la información contenida.
4. Se presenta una vista previa completa con los datos extraídos de cada bitácora para confirmación del usuario.
5. Al confirmar, los datos se almacenan en Firebase Firestore en la nube.
6. El usuario puede posteriormente buscar, filtrar y analizar los datos históricos.
7. Las herramientas de visualización permiten generar gráficos y mapas para auditorías MSC.

---

## 7. Conclusión

El sistema BENTOS representa una solución tecnológica efectiva para la automatización del procesamiento de bitácoras electrónicas de pesca en Pesquero Quintero S.A. El desarrollo abordó con éxito los desafíos técnicos inherentes a la extracción de datos desde documentos PDF con estructuras tabulares complejas y variables, implementando un motor de parsing robusto capaz de manejar tablas que se extienden entre múltiples páginas, lances con y sin captura, y diversos formatos de columnas.

La integración con Google Firebase Firestore proporciona un almacenamiento centralizado, escalable y accesible que cumple con los requisitos de retención de datos exigidos por la certificación MSC. Las herramientas de visualización, especialmente los mapas de calor georeferenciados y los indicadores de sostenibilidad ecosistémica, facilitan la preparación de las auditorías de certificación al presentar la información de manera clara, interactiva y profesional.

El sistema reemplaza un proceso manual que requería varias horas por viaje de pesca, reduciendo el tiempo de procesamiento a segundos por bitácora y eliminando los errores de transcripción. Adicionalmente, la centralización de datos permite análisis históricos y la detección de tendencias que antes no eran factibles.

Como líneas de trabajo futuro, se contempla la implementación de un sistema de autenticación de usuarios con roles diferenciados (administrador, capitán), la generación automática de reportes para auditorías MSC, y la posibilidad de acceso web remoto a los datos almacenados.

---

## 8. Bibliografía

Marine Stewardship Council. (2023). *MSC Fisheries Standard v3.0*. Marine Stewardship Council. https://www.msc.org/standards-and-certification/fisheries-standard

Servicio Nacional de Pesca y Acuicultura. (2020). *Resolución Exenta N° 1.800: Establece uso obligatorio de bitácora electrónica de pesca*. Sernapesca. https://www.sernapesca.cl

Subsecretaría de Pesca y Acuicultura. (2022). *Estado de situación de las principales pesquerías chilenas, año 2021*. Gobierno de Chile. https://www.subpesca.cl/portal/618/w3-propertyvalue-50834.html

Python Software Foundation. (2024). *Python 3.13 Documentation*. https://docs.python.org/3.13/

Google. (2024). *Firebase Admin Python SDK Documentation*. Google Cloud. https://firebase.google.com/docs/admin/setup

Jsvine, J. (2024). *pdfplumber: Plumb a PDF for detailed information about each text character, rectangle, and line*. GitHub. https://github.com/jsvine/pdfplumber

TomSchimansky. (2024). *CustomTkinter: A modern and customizable python UI-library based on Tkinter*. GitHub. https://github.com/TomSchimansky/CustomTkinter

McKinney, W. (2022). *Python for Data Analysis: Data Wrangling with pandas, NumPy, and Jupyter* (3ra ed.). O'Reilly Media.

Ley N° 20.657. (2013). *Modifica en el ámbito de la sustentabilidad de recursos hidrobiológicos, acceso a la actividad pesquera industrial y artesanal y regulaciones para la investigación y fiscalización, la Ley General de Pesca y Acuicultura*. Diario Oficial de la República de Chile. https://www.bcn.cl/leychile/navegar?idNorma=1049426
