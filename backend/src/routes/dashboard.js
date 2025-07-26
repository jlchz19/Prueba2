const express = require('express');
const router = express.Router();
const dashboardController = require('../controllers/dashboardController');
const { authenticateToken } = require('../middleware/auth');

// Obtener estadísticas del dashboard (requiere autenticación)
router.get('/stats', authenticateToken, dashboardController.getDashboardStats);

// Obtener actividad reciente (requiere autenticación)
router.get('/activity', authenticateToken, dashboardController.getRecentActivity);

module.exports = router; 