const User = require('../models/user');
const Product = require('../models/product');
const Category = require('../models/category');
const Provider = require('../models/provider');

// Obtener estadísticas del dashboard
exports.getDashboardStats = (req, res) => {
  // Obtener el user_id del token JWT
  const userId = req.user ? req.user.id : 1; // Por defecto usuario 1 si no hay token
  
  console.log('🔍 Dashboard - Usuario solicitando datos:', req.user);
  console.log('🔍 Dashboard - User ID:', userId);

  // Contar productos del usuario
  Product.countProducts(userId, (err, productsCount) => {
    if (err) {
      console.error('Error contando productos:', err);
      productsCount = 0;
    }

    // Contar categorías del usuario
    Category.countCategories(userId, (err, categoriesCount) => {
      if (err) {
        console.error('Error contando categorías:', err);
        categoriesCount = 0;
      }

      // Contar proveedores del usuario
      Provider.countProviders(userId, (err, providersCount) => {
        if (err) {
          console.error('Error contando proveedores:', err);
          providersCount = 0;
        }

        // Contar usuarios (solo 1 para el usuario logueado)
        const usersCount = 1;

        // Estadísticas del dashboard
        const stats = {
          products: productsCount,
          categories: categoriesCount,
          providers: providersCount,
          users: usersCount
        };

        res.json(stats);
      });
    });
  });
};

// Obtener actividad reciente
exports.getRecentActivity = (req, res) => {
  // Por ahora retornamos actividad simulada
  // En el futuro se puede implementar un sistema de logs real
  const recentActivity = [
    {
      id: 1,
      type: 'product',
      title: 'Nuevo producto agregado',
      description: 'Se agregó un producto al inventario',
      time: 'Hace 5 minutos'
    },
    {
      id: 2,
      type: 'category',
      title: 'Categoría actualizada',
      description: 'Se modificó una categoría del sistema',
      time: 'Hace 15 minutos'
    },
    {
      id: 3,
      type: 'provider',
      title: 'Proveedor registrado',
      description: 'Se agregó un nuevo proveedor',
      time: 'Hace 1 hora'
    },
    {
      id: 4,
      type: 'user',
      title: 'Usuario conectado',
      description: 'Un usuario inició sesión en el sistema',
      time: 'Hace 2 horas'
    }
  ];

  res.json(recentActivity);
}; 