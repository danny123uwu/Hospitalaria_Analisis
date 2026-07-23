# 🏥 Sistema Hospitalario (Fullstack Dockerizado)

Este proyecto consiste en un sistema hospitalario desarrollado con una arquitectura **Full Stack** utilizando **FastAPI** para el backend y **Angular** para el frontend. Todo el entorno se encuentra contenedorizado mediante **Docker** y **Docker Compose**, lo que permite ejecutar la aplicación de forma sencilla y consistente en cualquier equipo.

---

# 🚀 Tecnologías Utilizadas

- **Backend:** Python 3.10 + FastAPI + Uvicorn
- **Frontend:** Angular + Node.js 22 (Alpine)
- **Contenedores:** Docker & Docker Compose
- **Documentación de API:** Swagger UI
- **Pruebas de API:** Thunder Client

---

# 📁 Estructura del Proyecto

```text
hospital_backend/
│
├── hospital-frontend/        # Aplicación Angular
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── README.md
│
├── Dockerfile                # Backend FastAPI
├── docker-compose.yml        # Orquestación de contenedores
├── main.py
├── requirements.txt
└── README.md
```

---

# 📋 Requisitos Previos

Antes de ejecutar el proyecto debes tener instalado Docker.

## 🪟 Windows

- Docker Desktop
- Se recomienda habilitar **WSL2**
- Verificar que Docker Desktop esté en ejecución

## 🐧 Linux

- Docker Engine
- Docker Compose

Opcionalmente puedes agregar tu usuario al grupo `docker` para evitar utilizar `sudo`:

```bash
sudo usermod -aG docker $USER
```

> **Nota:** Es necesario cerrar sesión o reiniciar el equipo para aplicar el cambio.

---

# ⚙️ Ejecución del Proyecto

Ubícate en la carpeta raíz del proyecto (donde se encuentra el archivo `docker-compose.yml`).

## Primera ejecución

Construye las imágenes e inicia los contenedores:

```bash
docker compose up --build
```

## Ejecuciones posteriores

Si no realizaste cambios en los Dockerfiles o dependencias, simplemente ejecuta:

```bash
docker compose up
```

## Ejecutar en segundo plano

```bash
docker compose up -d
```

## Detener la aplicación

```bash
docker compose down
```

---

# 🌐 Acceso a la Aplicación

Una vez que ambos contenedores estén ejecutándose, podrás acceder a los siguientes servicios:

| Servicio | Dirección |
|-----------|-----------|
| Frontend (Angular) | http://localhost:4200 |
| Backend (FastAPI) | http://localhost:8000 |
| Documentación Swagger | http://localhost:8000/docs |

---

# 🧪 Pruebas de la API

La API puede probarse mediante **Thunder Client** o directamente desde **Swagger UI**.

### Thunder Client

1. Instalar la extensión en Visual Studio Code.
2. Crear una nueva petición.
3. Escribir la URL del endpoint.

Ejemplo:

```text
http://localhost:8000/
```

4. Seleccionar el método HTTP correspondiente (`GET`, `POST`, `PUT` o `DELETE`).
5. Presionar **Send**.

---

# 🛠️ Problemas Comunes

### Docker reutiliza imágenes antiguas

Si realizaste cambios importantes en dependencias o Dockerfiles, reconstruye completamente el proyecto:

```bash
docker compose down --volumes --remove-orphans
docker compose build --no-cache
docker compose up
```

---

### Error `Unsupported engine`

Verifica que el frontend utilice una imagen compatible con Angular:

```dockerfile
FROM node:22-alpine
```

---

### Angular no responde desde el navegador

Comprueba que el Dockerfile del frontend ejecute Angular con:

```dockerfile
CMD ["npm", "start", "--", "--host", "0.0.0.0"]
```

Esto permite que el servidor sea accesible desde fuera del contenedor.

---

# 🧹 Comandos Útiles

```bash
# Iniciar servicios
docker compose up

# Iniciar reconstruyendo imágenes
docker compose up --build

# Ejecutar en segundo plano
docker compose up -d

# Detener servicios
docker compose down

# Pausar contenedores
docker compose stop

# Reanudar contenedores
docker compose start

# Reiniciar contenedores
docker compose restart

# Ver el estado de los contenedores
docker compose ps

# Ver los registros en tiempo real
docker compose logs -f
```

---

# 📝 Notas Técnicas

Durante el desarrollo del proyecto se realizaron las siguientes configuraciones para garantizar el correcto funcionamiento del entorno Docker:

- Se actualizó el frontend para utilizar **Node.js 22**, compatible con la versión de Angular empleada.
- Se configuró Angular para escuchar en la dirección `0.0.0.0`, permitiendo el acceso desde el host.
- Se eliminó el atributo `version` del archivo `docker-compose.yml`, adaptándolo a la especificación moderna de Docker Compose.

Estas configuraciones permiten que el proyecto pueda ejecutarse correctamente tanto en Windows como en Linux.