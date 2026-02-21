# Guía de Logging con Elasticsearch + Kibana + Logstash - PharmaGo

## 📋 Configuración Implementada

### Stack de Logging Completo

**3 componentes:**
1. **Elasticsearch**: Almacenamiento y búsqueda de logs (puerto 9200)
2. **Kibana**: Visualización y consulta de logs (puerto 5601)
3. **Logstash**: Recopilación y procesamiento de logs (puerto 5044, 9600)

### Arquitectura

```
Contenedores Docker (stdout/stderr)
         ↓
    Archivos JSON de Docker
         ↓
    Logstash (lee y procesa logs)
         ↓
    Elasticsearch (almacena logs)
         ↓
    Kibana (visualiza logs)
```

## 🚀 Estado Actual

### Servicios Funcionando

- ✅ **Elasticsearch**: http://localhost:9200
- ✅ **Kibana**: http://localhost:5601
- ✅ **Logstash**: Recopilando logs de contenedores Docker

### Verificar que Funciona

1. **Accede a Kibana**: http://localhost:5601
2. **Crea un Index Pattern**:
   - Ve a **Management** → **Stack Management** → **Index Patterns**
   - Click en **Create index pattern**
   - Ingresa: `pharmago-logs-*`
   - Selecciona el campo de tiempo: `@timestamp`
   - Click en **Create index pattern**

3. **Ver Logs en Discover**:
   - Ve a **Discover** en el menú lateral
   - Selecciona el index pattern `pharmago-logs-*`
   - Deberías ver logs de tus servicios

## 📊 Cómo Usar los Logs

### 1. Ver Logs en Kibana

1. Accede a Kibana: http://localhost:5601
2. Ve a **Discover**
3. Selecciona el index pattern `pharmago-logs-*`
4. Verás todos los logs de tus servicios

### 2. Filtrar Logs por Servicio

En la barra de búsqueda de Kibana:

```
service: "pharmago-api-gateway"
service: "pharmago-users-service"
service: "pharmago-pharmacy-service"
```

### 3. Búsquedas Avanzadas

```
# Buscar errores
message: "Error" OR message: "Exception"

# Buscar por nivel de log
level: "Error"

# Combinar filtros
service: "pharmago-api-gateway" AND message: "Rate limit"
```

### 4. Verificar Logs en Elasticsearch

```powershell
# Verificar que hay logs indexados
Invoke-WebRequest -Uri "http://localhost:9200/pharmago-logs-*/_count" -UseBasicParsing

# Ver algunos logs
Invoke-WebRequest -Uri "http://localhost:9200/pharmago-logs-*/_search?size=5" -UseBasicParsing
```

## 🔧 Configuración Actual

### Logstash

- **Configuración**: `logstash/logstash.conf`
- **Input**: Lee archivos JSON de Docker (`/var/lib/docker/containers/*/*-json.log`)
- **Filter**: Procesa y enriquece logs
- **Output**: Envía a Elasticsearch con índice `pharmago-logs-YYYY.MM.dd`

### Elasticsearch

- **Puerto HTTP**: 9200
- **Puerto Transport**: 9300
- **Seguridad**: Deshabilitada (para desarrollo)
- **Memoria**: 512MB (configurable)

### Kibana

- **Puerto**: 5601
- **Conectado a**: Elasticsearch en http://elasticsearch:9200

## 📈 Crear Dashboards en Kibana

### Dashboard Básico de Logs

1. Ve a **Dashboard** → **Create Dashboard**
2. Agrega visualizaciones:
   - **Logs por servicio** (Pie chart)
   - **Logs en el tiempo** (Line chart)
   - **Top errores** (Data table)
   - **Logs recientes** (Logs viewer)

### Visualización: Logs por Servicio

1. **Visualize** → **Create Visualization** → **Pie**
2. Selecciona el index pattern `pharmago-logs-*`
3. Agrega un bucket: **Split slices**
4. Agrega términos por campo: `service.keyword`
5. Guarda la visualización

### Visualización: Logs en el Tiempo

1. **Visualize** → **Create Visualization** → **Line**
2. Selecciona el index pattern `pharmago-logs-*`
3. Agrega eje X: **Date Histogram** por `@timestamp`
4. Agrega eje Y: **Count**
5. Guarda la visualización

## 🔍 Troubleshooting

### Problema: No veo logs en Kibana

**Solución:**
1. Verifica que Logstash esté corriendo: `docker ps | grep logstash`
2. Verifica los logs de Logstash: `docker logs logstash`
3. Verifica que Elasticsearch tenga datos:
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:9200/pharmago-logs-*/_count" -UseBasicParsing
   ```
4. Verifica que el index pattern esté creado en Kibana

### Problema: Logstash no recopila logs

**Solución:**
1. Verifica que los contenedores estén generando logs:
   ```bash
   docker logs pharmago-api-gateway --tail 10
   ```
2. Verifica que Logstash tenga acceso a los archivos:
   ```bash
   docker exec logstash ls -la /var/lib/docker/containers/ | Select-Object -First 5
   ```
3. Revisa los logs de Logstash: `docker logs logstash`

### Problema: Elasticsearch no responde

**Solución:**
1. Verifica que Elasticsearch esté corriendo: `docker ps | grep elasticsearch`
2. Verifica los logs: `docker logs elasticsearch`
3. Verifica el health: http://localhost:9200/_cluster/health

## 📚 Recursos

- **Kibana Documentation**: https://www.elastic.co/guide/en/kibana/current/index.html
- **Elasticsearch Documentation**: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- **Logstash Documentation**: https://www.elastic.co/guide/en/logstash/current/index.html

## ✅ Checklist

- [x] Elasticsearch configurado y funcionando
- [x] Kibana configurado y funcionando
- [x] Logstash configurado y funcionando
- [ ] Index pattern creado en Kibana (`pharmago-logs-*`)
- [ ] Dashboard básico creado
- [ ] Logs verificados en Kibana

## 💡 Próximos Pasos

1. **Crear index pattern** en Kibana: `pharmago-logs-*`
2. **Explorar logs** en Discover
3. **Crear dashboards** personalizados
4. **Configurar alertas** (opcional)
