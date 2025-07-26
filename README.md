# Sistema de Gestión Web - Frontend Angular

Este proyecto es una interfaz web desarrollada en **Angular** que permite a los usuarios gestionar información a través de un sistema completo de autenticación y operaciones CRUD (Crear, Leer, Actualizar, Borrar). La aplicación está diseñada para conectarse a un backend realizado en **Node.js** (con base de datos SQLite), consumiendo sus endpoints para todas las operaciones.

## ✅ Requisitos cumplidos

✅ Frontend en Angular  
✅ Sistema de autenticación completo  
✅ CRUD para gestión de datos  
✅ Conexión con backend Node.js  
✅ Protección de rutas con tokens  
✅ Consumo de endpoints del backend

## 🚀 Características principales

### 🔐 Autenticación completa
- **Registro de nuevos usuarios** con validaciones robustas
- **Inicio de sesión** con validación de credenciales
- **Recuperación y restablecimiento de contraseña** vía correo electrónico
- **Verificación de email** con códigos de seguridad
- **Almacenamiento y uso de token JWT** para proteger rutas y mantener sesiones seguras

### 🛡️ Protección de rutas
- Solo los usuarios autenticados pueden acceder a las secciones protegidas
- El token se almacena en localStorage y se envía en cada petición protegida
- Redirección automática al login si el token expira o es inválido

### 📊 CRUD y filtrado por usuario
- **Crear, ver, editar y eliminar datos** (productos, categorías, proveedores, usuarios)
- Cada usuario solo puede ver y gestionar sus propios productos, categorías y proveedores
- Los administradores pueden gestionar todos los usuarios

### 🔗 Consumo de API
- Todas las acciones de autenticación y gestión de datos se comunican con el backend mediante peticiones HTTP
- Headers de autorización automáticos en todas las peticiones protegidas
- Manejo robusto de errores y respuestas del servidor

### 🎨 UI/UX moderna
- Diseño responsivo, moderno y atractivo
- Tarjetas (cards), sidebar colapsable, iconos y modales
- Experiencia de usuario mejorada en login, registro, recuperación de contraseña y dashboard
- Validaciones en tiempo real y feedback visual

## 🛠️ Tecnologías utilizadas

### Frontend
- **Angular 17** - Framework principal
- **TypeScript** - Lenguaje de programación
- **CSS3** - Estilos modernos y responsivos
- **HTML5** - Estructura semántica

### Backend
- **Node.js** - Runtime de JavaScript
- **Express.js** - Framework web
- **SQLite** - Base de datos
- **JWT** - Autenticación con tokens
- **Nodemailer** - Enví de emails

## 📁 Estructura del proyecto

```
src/
├── app/
│   ├── login/           # Componentes de autenticación
│   ├── register/        # Registro de usuarios
│   ├── verify-email/    # Verificación de email
│   ├── dashboard/       # Panel principal
│   ├── products/        # Gestión de productos
│   ├── categories/      # Gestión de categorías
│   ├── providers/       # Gestión de proveedores
│   ├── profile/         # Perfil de usuario
│   ├── settings/        # Configuraciones
│   ├── services/        # Servicios de API
│   └── shared/          # Componentes compartidos
├── environments/        # Configuración de ambientes
└── assets/             # Recursos estáticos
```

## 🚀 Instalación y ejecución

### Prerrequisitos
- Node.js (versión 16 o superior)
- npm o yarn
- Angular CLI

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/jlchz19/Prueba1.git
   cd Prueba1
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Iniciar la aplicación en modo desarrollo**
   ```bash
   npm start
   # o
   ng serve
   ```

4. **Abrir en el navegador**
   ```
   http://localhost:4200
   ```

### Configuración del backend

El frontend está configurado para conectarse al backend en:
```
https://prueba1-5jnd.onrender.com
```

Si necesitas cambiar la URL del backend, modifica el archivo:
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'https://tu-backend-url.com'
};
```

## 🔧 Funcionalidades detalladas

### Autenticación
- **Registro**: Validaciones de nombre, email y contraseña
- **Login**: Verificación de credenciales con manejo de errores
- **Recuperación de contraseña**: Enví de códigos por email
- **Verificación de email**: Confirmación de cuenta antes del primer login

### Gestión de datos
- **Productos**: CRUD completo con categorías
- **Categorías**: Gestión de categorías de productos
- **Proveedores**: Administración de proveedores
- **Perfil**: Actualización de información personal

### Seguridad
- **Tokens JWT**: Autenticación segura
- **Validaciones**: Sanitización de inputs
- **Protección de rutas**: Guardias de autenticación
- **Manejo de errores**: Respuestas específicas para cada tipo de error

## 📧 Recuperación de contraseña

1. En la pantalla de login, haz clic en "¿Olvidaste tu contraseña?"
2. Ingresa tu correo registrado y recibirás un email con un código
3. Ingresa el código y tu nueva contraseña
4. Confirma la nueva contraseña
5. Tu contraseña se actualizará automáticamente

## 🌐 Despliegue en Render

### Build Command
```bash
npm install && npm run build
```

### Publish Directory
```
dist/temp-frontend/browser
```

### Pasos rápidos
1. Sube tu código a GitHub
2. En Render, crea un nuevo Static Site
3. Conecta tu repositorio
4. Usa los comandos y carpeta especificados arriba
5. ¡Listo! Tu frontend estará en línea

## 🔍 Endpoints principales

### Autenticación
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Inicio de sesión
- `POST /api/auth/forgot` - Recuperación de contraseña
- `POST /api/auth/reset` - Restablecer contraseña
- `POST /api/auth/verify-email` - Verificar email
- `GET /api/auth/profile` - Obtener perfil
- `PUT /api/auth/profile` - Actualizar perfil

### CRUD
- `GET /api/productos` - Obtener productos
- `POST /api/productos` - Crear producto
- `PUT /api/productos/:id` - Actualizar producto
- `DELETE /api/productos/:id` - Eliminar producto

## 📝 Notas adicionales

- El sistema de autenticación utiliza tokens JWT para proteger las rutas
- El backend filtra los datos por usuario: cada usuario solo ve sus propios datos
- El diseño incluye sidebar colapsable, cards, modales y navegación mejorada
- Si tienes problemas con la recuperación de contraseña, revisa tu carpeta de spam
- Verifica que el backend esté corriendo y configurado correctamente

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**José Luis Chirinos**
- GitHub: [@jlchz19](https://github.com/jlchz19)

---

⭐ Si este proyecto te ha sido útil, ¡dale una estrella al repositorio!
