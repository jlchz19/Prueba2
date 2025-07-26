const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const User = require('../models/user');
const jwt = require('jsonwebtoken');
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

// Login
router.post('/login', authController.login);

// Registro
router.post('/register', authController.register);

// Verificación de email
router.post('/verify-email', authController.verifyEmail);

// Reenviar código de verificación
router.post('/resend-code', authController.resendCode);

// Recuperación de contraseña
router.post('/forgot', authController.forgot);
router.post('/reset', authController.reset);

// Obtener perfil del usuario
router.get('/profile', authMiddleware, (req, res) => {
  User.findById(req.user.id, (err, user) => {
    if (err) {
      return res.status(500).json({ message: 'Error al obtener perfil' });
    }
    
    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    res.json({
      id: user.id,
      name: user.name,
      email: user.email
    });
  });
});

// Actualizar perfil del usuario
router.put('/profile', authMiddleware, (req, res) => {
  const { name, email } = req.body;
  
  if (!name || !email) {
    return res.status(400).json({ message: 'Nombre y email son requeridos' });
  }

  // Verificar si el email ya existe en otro usuario
  User.findByEmail(email, (err, existingUser) => {
    if (err) {
      return res.status(500).json({ message: 'Error en el servidor' });
    }
    
    if (existingUser && existingUser.id !== req.user.id) {
      return res.status(400).json({ message: 'El email ya está en uso por otro usuario' });
    }

    // Actualizar usuario
    User.updateUser(req.user.id, name, email, 'user', (err, updatedUser) => {
      if (err) {
        return res.status(500).json({ message: 'Error al actualizar perfil' });
      }

      res.json({
        message: 'Perfil actualizado correctamente',
        user: { id: req.user.id, name, email }
      });
    });
  });
});

// Cambiar contraseña
router.put('/change-password', authMiddleware, (req, res) => {
  const { currentPassword, newPassword } = req.body;
  
  if (!currentPassword || !newPassword) {
    return res.status(400).json({ message: 'Contraseña actual y nueva son requeridas' });
  }

  if (newPassword.length < 6) {
    return res.status(400).json({ message: 'La nueva contraseña debe tener al menos 6 caracteres' });
  }

  // Obtener usuario actual
  User.findById(req.user.id, (err, user) => {
    if (err) {
      return res.status(500).json({ message: 'Error en el servidor' });
    }
    
    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    // Verificar contraseña actual
    User.validatePassword(user, currentPassword, (err, isMatch) => {
      if (err) {
        return res.status(500).json({ message: 'Error en el servidor' });
      }
      
      if (!isMatch) {
        return res.status(400).json({ message: 'La contraseña actual es incorrecta' });
      }

      // Actualizar contraseña
      User.updatePassword(req.user.id, newPassword, (err) => {
        if (err) {
          return res.status(500).json({ message: 'Error al cambiar contraseña' });
        }

        res.json({ message: 'Contraseña cambiada correctamente' });
      });
    });
  });
});

module.exports = router; 