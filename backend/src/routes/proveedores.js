const express = require('express');
const router = express.Router();
const db = require('../models/db');
const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'supersecreto';

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

// Obtener todos los proveedores del usuario autenticado
router.get('/', authMiddleware, (req, res) => {
  db.all('SELECT id, name as nombre, phone as telefono, user_id FROM providers WHERE user_id = ?', [req.user.id], (err, rows) => {
    if (err) return res.status(500).json({ message: 'Error al obtener proveedores' });
    res.json(rows);
  });
});

// Crear proveedor asociado al usuario autenticado
router.post('/', authMiddleware, (req, res) => {
  const { nombre, telefono } = req.body;
  db.run('INSERT INTO providers (name, phone, user_id) VALUES (?, ?, ?)',
    [nombre, telefono, req.user.id],
    function (err) {
      if (err) return res.status(500).json({ message: 'Error al crear proveedor' });
      res.status(201).json({ id: this.lastID, nombre, telefono });
    });
});

// Obtener proveedor por id (solo si pertenece al usuario)
router.get('/:id', authMiddleware, (req, res) => {
  db.get('SELECT id, name as nombre, phone as telefono, user_id FROM providers WHERE id=? AND user_id=?', [req.params.id, req.user.id], (err, row) => {
    if (err) return res.status(500).json({ message: 'Error al obtener proveedor' });
    if (!row) return res.status(404).json({ message: 'Proveedor no encontrado' });
    res.json(row);
  });
});

// Actualizar proveedor (solo si pertenece al usuario)
router.put('/:id', authMiddleware, (req, res) => {
  const { nombre, telefono } = req.body;
  db.run('UPDATE providers SET name=?, phone=? WHERE id=? AND user_id=?',
    [nombre, telefono, req.params.id, req.user.id],
    function (err) {
      if (err) return res.status(500).json({ message: 'Error al actualizar proveedor' });
      res.json({ id: req.params.id, nombre, telefono });
    });
});

// Eliminar proveedor (solo si pertenece al usuario)
router.delete('/:id', authMiddleware, (req, res) => {
  db.run('DELETE FROM providers WHERE id=? AND user_id=?', [req.params.id, req.user.id], function (err) {
    if (err) return res.status(500).json({ message: 'Error al eliminar proveedor' });
    res.json({ success: true });
  });
});

module.exports = router; 