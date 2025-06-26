<p align="center">
  <img src="https://github.com/4c1n0nyX/raizcom/blob/main/staticfiles/img/BANNER.jpg" alt="Logo RaízCom" width="500"/>
</p>

<h1 align="center">RaízCom - La Comunidad Móvil</h1>

<p align="center">
  Una plataforma de comunicación y gestión comunitaria diseñada para conectar, organizar y fortalecer a las comunidades.
  <br />
  <br />
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Django-4.2+-green.svg" alt="Django">
  <img src="https://img.shields.io/badge/Database-MariaDB-orange.svg" alt="MariaDB">
  <img src="https://img.shields.io/badge/Realtime-Django%20Channels-red.svg" alt="Django Channels">
  <img src="https://img.shields.io/badge/Platform-PWA-yellow.svg" alt="PWA">
</p>

---

## 🚀 Acerca del Proyecto

**RaízCom** es una aplicación multiplataforma que nace de la necesidad de fortalecer la comunicación y la organización en el **Consejo Comunal Raíces Fundamentales**. Su objetivo es ofrecer un punto centralizado para la interacción de los vecinos, la gestión transparente de recursos y la coordinación efectiva ante emergencias, poniendo "la comunidad móvil en la palma de tu mano".

Construida como una **Aplicación Web Progresiva (PWA)**, RaízCom combina la accesibilidad de un sitio web con la experiencia de una aplicación nativa, garantizando un bajo consumo de recursos y compatibilidad con una amplia gama de dispositivos (Android, iOS, Windows, Linux, macOS).

## ✨ Características Principales

Esta aplicación está equipada con un conjunto de módulos diseñados para potenciar la vida comunitaria:

* **📰 Muro de Noticias:** Un espacio centralizado donde los administradores y publicadores pueden compartir anuncios y noticias importantes que son visibles para toda la comunidad al iniciar sesión.
* **📦 Gestión de Recursos:** Permite la publicación y administración de recursos comunitarios como jornadas de alimentación (CLAP), gas, o eventos de salud. Los usuarios pueden reportar los pagos correspondientes y los administradores pueden generar reportes en PDF.
* **💬 Chat en Tiempo Real:** Un sistema de comunicación robusto que incluye:
    * Un **Chat General** para todos los miembros.
    * **Chats Privados** con los contactos de tu agenda.
* **🚨 Alertas de Emergencia Automatizadas:** Un bot integrado que monitorea fuentes oficiales y publica alertas sobre eventos climáticos y sísmicos en todo el territorio nacional, manteniendo a la comunidad prevenida.
* **🗺️ Servicios Geolocalizados:** Un mapa interactivo donde se pueden visualizar y filtrar por categoría los servicios de la comunidad, como farmacias, centros de salud, comercios y módulos policiales.
* **👥 Gestión de Usuarios y Roles:** Un sistema de permisos flexible con tres niveles:
    * **Administrador:** Control total del sistema.
    * **Publicador:** Permisos para gestionar noticias y recursos.
    * **Estándar:** Permisos de visualización y participación.
* **👤 Perfil de Usuario Personalizable:** Cada usuario puede editar su información personal, cambiar su contraseña y foto de perfil.

## 💻 Tech Stack

La aplicación está construida con un stack de tecnologías moderno, robusto y escalable:

* **Backend:** Django (Python)
* **Frontend:** HTML, CSS, JavaScript (Renderizado del lado del servidor)
* **Base de Datos:** MariaDB
* **Comunicación en Tiempo Real:** Django Channels
* **Servidor de Caché:** Redis
* **Servidor de Aplicaciones ASGI:** Daphne
* **Proxy Inverso (Producción):** Nginx

---

## 🛠️ Guía de Despliegue en Servidor Linux (Ubuntu/Debian)

Esta guía detalla los pasos para instalar y desplegar la aplicación en un entorno de producción, basada en el manual de despliegue.

### **Requisitos de Servidor**
* **SO:** Linux (Ubuntu 22.04 LTS / Debian 12 recomendado)
* **CPU:** 4+ núcleos
* **RAM:** 8 GB+
* **Almacenamiento:** 50 GB+ SSD
* **Python:** 3.8+
* **MariaDB:** 10.6+

### **Fase 1: Instalación de Dependencias del Sistema**

1.  **Actualizar el Sistema:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

2.  **Instalar Python, Git y Herramientas de Compilación:**
    ```bash
    sudo apt install python3 python3-pip python3-venv git python3-dev default-libmysqlclient-dev build-essential pkg-config weasyprint -y
    ```

3.  **Instalar MariaDB Server:**
    ```bash
    sudo apt install mariadb-server libmariadb-dev-compat libmariadb-dev -y
    ```

4.  **Instalar Redis Server:**
    ```bash
    sudo apt install redis-server -y
    ```

### **Fase 2: Configuración de la Base de Datos**

1.  **Asegurar la instalación de MariaDB:**
    ```bash
    sudo mysql_secure_installation
    ```
    (Sigue las instrucciones para establecer una contraseña de root).

2.  **Crear la Base de Datos y el Usuario:**
    ```bash
    sudo mysql -u root -p
    ```
    Dentro de la consola de MariaDB, ejecuta:
    ```sql
    CREATE DATABASE raizcom CHARACTER SET UTF8MB4 COLLATE utf8mb4_general_ci;
    CREATE USER 'raizcom_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
    GRANT ALL PRIVILEGES ON raizcom.* TO 'raizcom_user'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
    ```

### **Fase 3: Instalación de la Aplicación**

1.  **Clonar el Repositorio:**
    ```bash
    git clone https://github.com/4c1n0nyX/raizcom.git /opt/RAIZCOM
    cd /opt/RAIZCOM
    ```

2.  **Crear y Activar el Entorno Virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar Dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la Conexión a la Base de Datos:**
    Edita el archivo `app/settings.py` y modifica la sección `DATABASES` con los datos creados en la Fase 2.

5.  **Cargar Datos Iniciales y Aplicar Migraciones:**
    ```bash
    # (Opcional) Carga el dump de la BD si lo tienes
    mysql -u raizcom_user -p raizcom < raizcom.sql

    # Aplica las migraciones de Django
    python manage.py migrate

    # Recolecta los archivos estáticos
    python manage.py collectstatic
    ```
6.  **Modificar API KEY de OpenWeatherMap:**
    Edita el archivo `app/settings.py` y modifica la variable `OPENWEATHER_API_KEY` con la KEY que genera OpenWeatherMap. Para ello debes registrarte en https://openweathermap.org/
    
### **Fase 4: Puesta en Marcha y Configuración Inicial**

1.  **Crear los Grupos de Roles:**
    ```bash
    python manage.py create_initial_groups
    ```

2.  **Crear el Usuario del Bot de Alertas:**
    ```bash
    export ALERTAS_BOT_PASSWORD="TuContraseñaSeguraParaElBot"
    python manage.py create_alertas_bot
    ```

3.  **Crear un Usuario Administrador:**
    ```bash
    python manage.py create_admin_user tu_cedula
    ```
    (Te pedirá una contraseña).

4.  **Ejecutar los Servicios:**
    * **Bot de Alertas (en segundo plano):**
        ```bash
        nohup python manage.py run_sismo_bot > /var/log/raizcom_alert.log 2>&1 &
        ```
    * **Servidor de Aplicaciones Daphne (en segundo plano):**
        ```bash
        nohup daphne app.asgi:application -b 0.0.0.0 -p 8000 > /var/log/raizcom.log 2>&1 &
        ```

¡Tu aplicación ahora debería estar corriendo! Puedes acceder a ella a través de la IP de tu servidor en el puerto 8000. Para un despliegue en producción, se recomienda configurar un proxy inverso como Nginx y un certificado SSL.

## 🖼️ Galería

| Inicio de Sesión | Dashboard Principal | Mapa de Servicios |
| :---: | :---: | :---: |
| *<img src="https://github.com/4c1n0nyX/raizcom/blob/main/staticfiles/img/LOGIN.jpg">* | *<img src="https://github.com/4c1n0nyX/raizcom/blob/main/staticfiles/img/DASHBOARD.jpg">* | *<img src="https://github.com/4c1n0nyX/raizcom/blob/main/staticfiles/img/SERVICIOS.jpg">* |


## ✍️ Autores

* **Angelo Camacho** - *Desarrollo y Documentación* - [24723277]
* **Miguel Márquez** - *Desarrollo y Documentación* - [18442329]

---
