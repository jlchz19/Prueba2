const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const authRoutes = require('./routes/auth');
const productosRoutes = require('./routes/productos');
const categoriasRoutes = require('./routes/categorias');
const proveedoresRoutes = require('./routes/proveedores');
const dashboardRoutes = require('./routes/dashboard');
const settingsRoutes = require('./routes/settings');

// Cargar variables de entorno
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Configuración de CORS
const allowedOrigins = [
  'https://frontend-con-angular.onrender.com', 
  'http://localhost:4200', 
  'http://localhost:52101',
  'https://backen4-1.onrender.com',
  'https://prueba2-3bij.onrender.com',
  'https://prueba2-fmmr.onrender.com'  // Added new frontend domain
];
app.use(cors({
  origin: function (origin, callback) {
    // Permitir solicitudes sin origen (como Postman) o desde el frontend permitido
    if (!origin || allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      console.log('Origen bloqueado por CORS:', origin);
      callback(new Error('No permitido por CORS'));
    }
  },
  credentials: true
}));
app.use(bodyParser.json());

// Rutas principales
app.use('/api/auth', authRoutes);
app.use('/api/productos', productosRoutes);
app.use('/api/categorias', categoriasRoutes);
app.use('/api/proveedores', proveedoresRoutes);
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/settings', settingsRoutes);
// Aquí se agregarán las rutas de productos, categorías y proveedores

app.get('/', (req, res) => {
  res.send('API funcionando');
});

app.listen(PORT, () => {
  console.log(`Servidor backend escuchando en http://localhost:${PORT}`);
}); 