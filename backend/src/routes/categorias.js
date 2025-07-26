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

// Obtener todas las categorías del usuario autenticado
router.get('/', authMiddleware, (req, res) => {
  db.all('SELECT id, name as nombre, description as descripcion, user_id FROM categories WHERE user_id = ?', [req.user.id], (err, rows) => {
    if (err) return res.status(500).json({ message: 'Error al obtener categorías' });
    res.json(rows);
  });
});

// Crear categoría asociada al usuario autenticado
router.post('/', authMiddleware, (req, res) => {
  const { nombre, descripcion } = req.body;
  db.run('INSERT INTO categories (name, description, user_id) VALUES (?, ?, ?)',
    [nombre, descripcion, req.user.id],
    function (err) {
      if (err) return res.status(500).json({ message: 'Error al crear categoría' });
      res.status(201).json({ id: this.lastID, nombre, descripcion });
    });
});

// Obtener categoría por id (solo si pertenece al usuario)
router.get('/:id', authMiddleware, (req, res) => {
  db.get('SELECT id, name as nombre, description as descripcion, user_id FROM categories WHERE id=? AND user_id=?', [req.params.id, req.user.id], (err, row) => {
    if (err) return res.status(500).json({ message: 'Error al obtener categoría' });
    if (!row) return res.status(404).json({ message: 'Categoría no encontrada' });
    res.json(row);
  });
});

// Actualizar categoría (solo si pertenece al usuario)
router.put('/:id', authMiddleware, (req, res) => {
  const { nombre, descripcion } = req.body;
  db.run('UPDATE categories SET name=?, description=? WHERE id=? AND user_id=?',
    [nombre, descripcion, req.params.id, req.user.id],
    function (err) {
      if (err) return res.status(500).json({ message: 'Error al actualizar categoría' });
      res.json({ id: req.params.id, nombre, descripcion });
    });
});

// Eliminar categoría (solo si pertenece al usuario)
router.delete('/:id', authMiddleware, (req, res) => {
  db.run('DELETE FROM categories WHERE id=? AND user_id=?', [req.params.id, req.user.id], function (err) {
    if (err) return res.status(500).json({ message: 'Error al eliminar categoría' });
    res.json({ success: true });
  });
});

module.exports = router; 