# Sistema de Gestión Web - Frontend Angular

Este proyecto es una interfaz web desarrollada en **Angular** que permite a los usuarios gestionar información a través de un sistema completo de autenticación y operaciones CRUD (Crear, Leer, Actualizar, Borrar). La aplicación está diseñada para conectarse a un backend realizado en **Node.js** (con base de datos SQLite), consumiendo sus endpoints para todas las operaciones.

## Características principales

- **Autenticación completa:**
  - Registro de nuevos usuarios.
  - Inicio de sesión con validación de credenciales.
  - Recuperación y restablecimiento de contraseña vía correo electrónico.
  - Almacenamiento y uso de token JWT para proteger rutas y mantener sesiones seguras.
- **Protección de rutas:**
  - Solo los usuarios autenticados pueden acceder a las secciones protegidas de la aplicación.
  - El token se almacena en localStorage y se envía en cada petición protegida.
- **CRUD y filtrado por usuario:**
  - Permite crear, ver, editar y eliminar datos (productos, categorías, proveedores, usuarios).
  - Cada usuario solo puede ver y gestionar sus propios productos, categorías y proveedores.
  - Los administradores pueden gestionar todos los usuarios.
- **Consumo de API:**
  - Todas las acciones de autenticación y gestión de datos se comunican con el backend mediante peticiones HTTP.
- **UI/UX moderna:**
  - Diseño responsivo, moderno y atractivo con tarjetas (cards), sidebar colapsable, iconos y modales.
  - Experiencia de usuario mejorada en login, registro, recuperación de contraseña y dashboard.

---

## ¿Cómo ejecutar la página localmente?

1. Abre una terminal y navega a la carpeta del frontend:
   ```bash
   cd FrontEndAngular-main
   ```
2. Instala las dependencias:
   ```bash
   npm install
   ```
3. Inicia la aplicación en modo desarrollo:
   ```bash
   npm start
   ```
   o también puedes usar:
   ```bash
   ng serve
   ```
4. Abre tu navegador y entra a:
   ```
   http://localhost:4200
   ```

**Recuerda:**
- El frontend estará disponible en `http://localhost:4200`
- El backend estará disponible en `https://prueba1-5jnd.onrender.com`
- Para iniciar el backend:
  ```bash
  cd backend
  npm install
  node src/app.js
  ```

---

## Recuperación de contraseña

1. En la pantalla de login, haz clic en "¿Olvidaste tu contraseña?".
2. Ingresa tu correo registrado y recibirás un email con un enlace para restablecer tu contraseña.
3. Haz clic en el enlace del correo, ingresa tu nueva contraseña y confírmala.
4. Si el token es válido, tu contraseña se actualizará en el sistema y podrás iniciar sesión normalmente.

---

## Despliegue en Render

### Build Command
```bash
npm install && npm run build
```

### Publish Directory
```
dist/temp-frontend/browser
```

### Pasos rápidos
1. Sube tu código a GitHub.
2. En Render, crea un nuevo Static Site y conecta tu repo.
3. Usa los comandos y carpeta de arriba.
4. ¡Listo! Tu frontend estará en línea y conectado al backend.

---

## Notas adicionales
- El sistema de autenticación utiliza tokens JWT para proteger las rutas y las operaciones sensibles.
- El backend filtra los datos por usuario: cada usuario solo ve y gestiona sus propios productos, categorías y proveedores.
- El diseño moderno incluye sidebar colapsable, cards, modales y navegación mejorada.
- Si tienes problemas con la recuperación de contraseña, revisa tu carpeta de spam o verifica que el backend esté corriendo y configurado con las credenciales de correo.
