# 📊 Manual de Búsqueda y Análisis MSC - BENTOS

## 🔍 Funcionalidades de Búsqueda Mejoradas

### Filtros Disponibles

#### 1. **🆔 ID de Viaje (Folio)**
- Busca un viaje específico por su Folio SERNAPESCA
- Ejemplo: `SERNAPESCA-BE2021-3088-1`
- Soporta búsqueda parcial (no case-sensitive)

#### 2. **📅 Rango de Fechas con Calendario**
- **Fecha Desde / Fecha Hasta**: Selecciona fechas usando calendarios interactivos
- **Botones Rápidos**:
  - 🗓️ **Mes actual**: Filtra todas las bitácoras del mes en curso
  - 📆 **Año actual**: Filtra todas las bitácoras del año en curso
- Formato: DD/MM/AAAA

#### 3. **🚢 Filtro por Nave**
- Filtra bitácoras por embarcación específica
- Opciones: "Todas" o nombres de naves disponibles

#### 4. **🦐 Filtro por Especie Objetivo**
- Filtra por especie objetivo de la faena
- Opciones:
  - Todas
  - Camarón nailon
  - Langostino colorado

#### 5. **🚦 Filtro por Alerta Ecosistema**
- Filtra según el nivel de alerta MSC
- Opciones:
  - 🟢 **Verde**: Ratio Merluza/Camarón ≤ 10%
  - 🟡 **Amarillo**: Ratio entre 10% - 20%
  - 🔴 **Rojo**: Ratio > 20%

---

## 📊 Estadísticas Automáticas

Al activar **"Calcular totales de captura"** (activado por defecto), el sistema muestra:

### Panel de Estadísticas Incluye:

#### 📈 Totales Principales
- **🚢 Viajes**: Cantidad de viajes filtrados
- **🎣 Lances**: Total de lances realizados
- **🦐 Camarón nailon**: Total capturado en TON
- **🐟 Merluza común**: Total capturado en TON

#### 🦞 Especies Secundarias
- **Langostino**: Total capturado
- **Lenguado**: Total capturado

#### 🎯 Indicadores MSC
- **📊 Ratio Merluza/Camarón**: Porcentaje calculado
- **🚦 Alerta Ecosistema**: Estado general del período

---

## 💡 Casos de Uso

### Caso 1: Análisis Mensual
**Objetivo**: Calcular cuánto se pescó en enero 2021

1. Click en **"Mes actual"** (o selecciona fechas manualmente)
2. Activa **"Calcular totales de captura"** ✅
3. Click en **"🔍 Buscar y Analizar"**
4. Revisa el panel de estadísticas superior

### Caso 2: Buscar Viaje Específico
**Objetivo**: Encontrar datos de un folio específico

1. Ingresa el Folio en **"ID de Viaje"**
2. Click en **"🔍 Buscar y Analizar"**
3. Click en **"📊 Ver detalles completos"**

### Caso 3: Auditoría por Alerta Roja
**Objetivo**: Encontrar todos los viajes con alerta roja

1. Selecciona **🔴 Rojo** en "Alerta Ecosistema"
2. Define rango de fechas (ej: año completo)
3. Click en **"🔍 Buscar y Analizar"**
4. Exporta resultados para informe

### Caso 4: Análisis por Embarcación
**Objetivo**: Ver totales de una nave específica

1. Selecciona la nave en el filtro **🚢 Nave**
2. Define período (mes, año, o rango personalizado)
3. Activa cálculo de totales
4. Click en **"🔍 Buscar y Analizar"**

---

## 🎨 Tarjetas de Resultados

Cada viaje muestra:
- 📋 **Folio SERNAPESCA**
- 📅 **Fecha y hora de zarpe**
- 🚢 **Nombre de la nave**
- 👨‍✈️ **Capitán**
- 🏢 **Armador**
- 🦐 **Total Camarón** (TON)
- 🐟 **Total Merluza** (TON)
- 📊 **Ratio calculado**
- 🚦 **Alerta ecosistema** (Verde/Amarillo/Rojo)

---

## 🔄 Botones de Acción

### 🔍 Buscar y Analizar
- Ejecuta la búsqueda con los filtros seleccionados
- Muestra resultados y estadísticas

### 🔄 Limpiar
- Resetea todos los filtros
- Limpia resultados
- Restablece fechas al mes actual

### 📊 Exportar Excel
- ⚠️ **Próximamente**: Exportará resultados filtrados a Excel
- Incluirá estadísticas y análisis MSC completo

---

## 📐 Cálculos MSC

### Ratio Merluza/Camarón
```
Ratio (%) = (Total Merluza TON / Total Camarón TON) × 100
```

### Niveles de Alerta
| Ratio | Alerta | Descripción |
|-------|--------|-------------|
| ≤ 10% | 🟢 VERDE | Pesca sostenible |
| 10-20% | 🟡 AMARILLO | Precaución |
| > 20% | 🔴 ROJO | Nivel crítico |

---

## 💾 Datos Guardados

Cada bitácora almacena:
- ✅ Información del viaje (nave, capitán, armador, fechas)
- ✅ Detalles de cada lance (coordenadas, hora, profundidad)
- ✅ Especies capturadas (nombre, cantidad, tipo)
- ✅ Cálculos MSC automáticos
- ✅ Validación de datos

---

## 🚀 Próximas Funcionalidades

- [ ] Exportación a Excel con gráficos
- [ ] Visualización en mapa de coordenadas de pesca
- [ ] Comparación entre períodos
- [ ] Alertas automáticas por email
- [ ] Dashboard ejecutivo con KPIs

---

## 📞 Soporte

Para consultas sobre el uso del sistema:
- Revisar la integridad de datos con `verificar_integridad.py`
- Consultar archivos de log en `data/output/`
- Verificar conexión Firebase

---

**Versión**: 2.0  
**Última actualización**: Enero 2025  
**Sistema**: BENTOS - Marine Stewardship Council Compliance
