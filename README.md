# 🏥 Sistema Hospitalario (Fullstack Dockerizado)

Este proyecto cuenta con una arquitectura fullstack totalmente contenedorizada utilizando **Docker** y **Docker Compose**. Combina un backend en **FastAPI (Python)** y un frontend moderno en **Angular**.

---

## 🚀 Tecnologías y Herramientas

- **Backend:** Python 3.10 + FastAPI + Uvicorn
- **Frontend:** Angular + Node.js 22 (Alpine)
- **Orquestación:** Docker & Docker Compose
- **Pruebas de API:** Thunder Client / Swagger UI

---

## 🛠️ Historia del Proyecto y Problemas Resueltos

Durante el proceso de configuración y despliegue del entorno con Docker, se solucionaron los siguientes desafíos técnicos:

### 1. Incompatibilidad de Node.js con Angular

**Problema:** El frontend fallaba o mostraba advertencias de `Unsupported engine` al intentar instalar dependencias sobre una imagen base `node:18-alpine`.

**Solución:** Se actualizó el `Dockerfile` del frontend a `node:22-alpine` para cumplir con los requisitos de la versión de Angular utilizada.

### 2. Exposición del Servidor de Desarrollo de Angular

**Problema:** El frontend no respondía fuera del contenedor al ejecutar `ng serve`.

**Solución:** Se configuró el comando de arranque con la opción `--host 0.0.0.0`.

```dockerfile
CMD ["npm", "start", "--", "--host", "0.0.0.0"]
```

Esto permite que las peticiones desde el host lleguen correctamente al contenedor.

### 3. Optimización de Docker Compose

**Problema:** Advertencias relacionadas con el atributo obsoleto `version` en `docker-compose.yml`.

**Solución:** Se eliminó dicho atributo para adaptarse a la especificación moderna de Docker Compose.

---

# 📋 Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado Docker según tu sistema operativo.

## 🪟 Windows

- Tener instalado **Docker Desktop**.
- Se recomienda habilitar **WSL2**.
- Verificar que Docker Desktop esté iniciado.

## 🐧 Linux (Ubuntu, Debian, Fedora, etc.)

- Tener instalados **Docker Engine** y **Docker Compose**.
- *(Opcional)* Agregar el usuario al grupo `docker` para evitar usar `sudo`:

```bash
sudo usermod -aG docker $USER
```

> **Nota:** Es necesario cerrar sesión o reiniciar el equipo para aplicar el cambio.

---

# ⚙️ Cómo Ejecutar la Aplicación

Ubícate en la carpeta raíz del proyecto, donde se encuentra el archivo `docker-compose.yml`.

## 1. Construir y levantar los contenedores

```bash
docker compose up --build
```

## 2. Ejecutar en segundo plano (Detached Mode)

```bash
docker compose up -d --build
```

## 3. Detener los contenedores

Si ejecutaste el proyecto en modo interactivo:

- Presiona **Ctrl + C**.

Si lo ejecutaste en segundo plano:

```bash
docker compose down
```

---

# 🌐 Puertos y Enlaces de Acceso

Una vez iniciados los servicios, estarán disponibles en las siguientes direcciones:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:4200 | Aplicación Angular |
| Backend API | http://localhost:8000 | API REST con FastAPI |
| Swagger UI | http://localhost:8000/docs | Documentación interactiva |

---

# 🧪 Pruebas de Endpoints con Thunder Client

1. Instala la extensión **Thunder Client** en Visual Studio Code.
2. Crea una **New Request**.
3. Ingresa la URL del endpoint, por ejemplo:

```text
http://localhost:8000/
```

4. Selecciona el método HTTP correspondiente (`GET`, `POST`, `PUT` o `DELETE`).
5. Haz clic en **Send**.

---

# 🧹 Comandos Útiles

```bash
# Detener y eliminar contenedores junto con sus redes
docker compose down

# Ver el estado de los contenedores
docker compose ps

# Ver los logs en tiempo real
docker compose logs -f
```