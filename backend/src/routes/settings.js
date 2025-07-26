const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const db = require('../models/db');
const JWT_SECRET = process.env.JWT_SECRET || 'supersecreto';

// Middleware de autenticación
function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader) return res.status(401).json({ message: 'Token requerido' });
  const token = authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ message: 'Token inválido' });
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ message: 'Token inválido' });
    req.user = user;
    next();
  });
}

// Obtener configuración del usuario
router.get('/', authMiddleware, (req, res) => {
  db.get('SELECT settings FROM users WHERE id = ?', [req.user.id], (err, user) => {
    if (err) {
      return res.status(500).json({ message: 'Error al obtener configuración' });
    }
    
    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    let settings = {};
    if (user.settings) {
      try {
        settings = JSON.parse(user.settings);
      } catch (e) {
        settings = {};
      }
    }

    // Configuración por defecto
    const defaultSettings = {
      notifications: {
        email: true,
        push: false,
        system: true
      },
      appearance: {
        theme: 'light',
        language: 'es',
        fontSize: 'medium'
      },
      security: {
        twoFactor: false,
        sessionTimeout: 30,
        autoLogout: true
      },
      data: {
        autoBackup: true,
        backupFrequency: 'daily',
        retentionDays: 30
      }
    };

    // Combinar configuración guardada con valores por defecto
    const finalSettings = { ...defaultSettings, ...settings };
    res.json(finalSettings);
  });
});

// Actualizar configuración del usuario
router.put('/', authMiddleware, (req, res) => {
  const settings = req.body;
  
  if (!settings) {
    return res.status(400).json({ message: 'Configuración requerida' });
  }

  const settingsJson = JSON.stringify(settings);
  
  db.run('UPDATE users SET settings = ? WHERE id = ?',
    [settingsJson, req.user.id],
    function(err) {
      if (err) {
        return res.status(500).json({ message: 'Error al guardar configuración' });
      }

      res.json({ 
        message: 'Configuración guardada correctamente',
        settings: settings
      });
    }
  );
});

// Exportar datos del usuario
router.get('/export', authMiddleware, (req, res) => {
  // Obtener datos del usuario
  db.get('SELECT id, name, email, created_at FROM users WHERE id = ?', [req.user.id], (err, user) => {
    if (err) {
      return res.status(500).json({ message: 'Error al exportar datos' });
    }
    
    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    // Obtener configuración
    db.get('SELECT settings FROM users WHERE id = ?', [req.user.id], (err, settingsRow) => {
      if (err) {
        return res.status(500).json({ message: 'Error al exportar configuración' });
      }

      let settings = {};
      if (settingsRow && settingsRow.settings) {
        try {
          settings = JSON.parse(settingsRow.settings);
        } catch (e) {
          settings = {};
        }
      }

      // Crear objeto de exportación
      const exportData = {
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          created_at: user.created_at
        },
        settings: settings,
        export_date: new Date().toISOString(),
        version: '2.0.0'
      };

      res.json(exportData);
    });
  });
});

module.exports = router; 