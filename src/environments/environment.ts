// Configuración del entorno - FORZAR ACTUALIZACIÓN
export const environment = {
  production: false,
  apiUrl: 'https://prueba1-5jnd.onrender.com',
  version: '1.0.6',
  timestamp: Date.now(),
  forceUpdate: true,
  cacheBuster: Math.random().toString(36).substring(7),
  debug: true
}; 