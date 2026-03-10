# Inicio Rápido

## Requisitos
- Docker y Docker Compose
- .NET 6.0 SDK (opcional, solo para desarrollo local sin Docker)

## Levantar la Aplicación Completa

### Con Docker Compose (Recomendado - Levanta TODO)

```bash
docker-compose up --build
```

Esto levanta automáticamente:
- Base de datos SQL Server
- Users Service
- Pharmacy Service  
- API Gateway
- Frontend Angular
- Prometheus
- Grafana
- Elasticsearch
- Kibana
- Logstash
- OpenTelemetry Collector

### Acceso a Servicios

- **Frontend**: http://localhost:4200
- **API Gateway**: http://localhost:5000
- **Users Service**: http://localhost:5001
- **Pharmacy Service**: http://localhost:5002
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
  - Datasource de Prometheus pre-configurado
  - Dashboard "PharmaGo - Overview" incluido
- **Kibana**: http://localhost:5601
  - Visualización y análisis de logs de la aplicación

### Persistencia de Datos

Los datos se mantienen al reiniciar:

```bash
# Apagar servicios (datos se mantienen)
docker-compose down

# Volver a levantar (datos restaurados)
docker-compose up -d

# Apagar y eliminar TODOS los datos
docker-compose down -v
```

**Datos persistentes:**
- Base de datos SQL Server (usuario sa, contraseña Str0ngP@ssword!)
- Métricas de Prometheus (30 días)
- Dashboards de Grafana

### Conectar a la Base de Datos (SQL Server Management Studio)

Para conectarte a la base de datos con SSMS cuando la app corre con Docker Compose:

- **Server name:** `localhost,11433`
- **Autenticación:** SQL Server Authentication
- **Login:** `sa`
- **Password:** `Str0ngP@ssword!`
- **Base de datos:** `PharmaDb`

Asegúrate de que el contenedor de la base de datos esté levantado (`docker-compose up -d pharmago-db`).

### Datos Iniciales (Seed)

La app necesita roles y datos base. Ejecuta el script de seed después de levantar la aplicación:

1. Levanta la app (al menos la DB): `docker-compose up -d` o `docker-compose up pharmago-db`
2. Conecta SSMS a `localhost,11433` (ver apartado anterior)
3. Abre `Backend/seed-data.sql` en SSMS
4. Ejecuta el script (F5)

El script inserta:
- **Roles:** Administrator, Employee, Owner (obligatorios para la app)
- **UnitMeasures y Presentations** para medicamentos
- **Farmacia de ejemplo**
- **Usuarios de prueba:** `admin`, `owner001`, `empleado01` (password: `Abcdef12.`)
- **Invitación** para registro: usuario `nuevo_empleado`, código `123456`
- **Medicamentos de ejemplo**

Puedes ejecutarlo varias veces sin duplicar datos (usa `IF NOT EXISTS`).

---

## Desarrollo Local (Sin Docker - Opcional)

Solo si necesitas desarrollar/debuggear servicios individuales en tu IDE:

#### 1. Base de datos
```bash
docker-compose up pharmago-db
```

#### 2. Users Service
```bash
cd Backend/PharmaGo.UsersService
dotnet restore
dotnet run
```

#### 3. Pharmacy Service (nueva terminal)
```bash
cd Backend/PharmaGo.PharmacyService
dotnet restore
dotnet run
```

#### 4. API Gateway (nueva terminal)
```bash
cd Backend/PharmaGo.ApiGateway
dotnet restore
dotnet run
```

#### 5. Frontend (nueva terminal)
```bash
cd Frontend
npm install
npm start
```

## Detener Servicios

```bash
docker-compose down
```

## Ejecutar Tests

```bash
cd Backend/PharnaGo.Test
dotnet test
```

## Verificar Prometheus

```bash
# Acceder a Prometheus Targets
http://localhost:9090/targets

# Verificar métricas directamente
curl http://localhost:5000/metrics
curl http://localhost:5001/metrics
curl http://localhost:5002/metrics
```

