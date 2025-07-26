const express = require('express');
const router = express.Router();
const db = require('../models/db');
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

// Obtener todos los productos del usuario autenticado
router.get('/', authMiddleware, (req, res) => {
  db.all('SELECT id, name as nombre, category_id as categoria, description as descripcion, price as precio, user_id FROM products WHERE user_id = ?', [req.user.id], (err, rows) => {
    if (err) return res.status(500).json({ message: 'Error al obtener productos' });
    res.json(rows);
  });
});

// Crear producto asociado al usuario autenticado
router.post('/', authMiddleware, (req, res) => {
  const { nombre, categoria, descripcion, precio } = req.body;
  db.run('INSERT INTO products (name, category_id, description, price, user_id) VALUES (?, ?, ?, ?, ?)',
    [nombre, categoria, descripcion, precio, req.user.id],
    function (err) {
      if (err) return res.status(500).json({ message: 'Error al crear producto' });
      res.status(201).json({ id: this.lastID, nombre, categoria, descripcion, precio });
    });
});

// Obtener producto por id (solo si pertenece al usuario)
router.get('/:id', authMiddleware, (req, res) => {
  db.get('SELECT id, name as nombre, category_id as categoria, description as descripcion, price as precio, user_id FROM products WHERE id=? AND user_id=?', [req.params.id, req.user.id], (err, row) => {
    if (err) return res.status(500).json({ message: 'Error al obtener producto' });
    if (!row) return res.status(404).json({ message: 'Producto no encontrado' });
    res.json(row);
  });
});

// Actualizar producto (solo si pertenece al usuario)
router.put('/:id', authMiddleware, (req, res) => {
  const { nombre, categoria, descripcion, precio } = req.body;
  db.run('UPDATE products SET name=?, category_id=?, description=?, price=? WHERE id=? AND user_id=?',
    [nombre, categoria, descripcion, precio, req.params.id, req.user.id],
    function (err) {
      if (err) return res.status(500).json({ message: 'Error al actualizar producto' });
      res.json({ id: req.params.id, nombre, categoria, descripcion, precio });
    });
});

// Eliminar producto (solo si pertenece al usuario)
router.delete('/:id', authMiddleware, (req, res) => {
  db.run('DELETE FROM products WHERE id=? AND user_id=?', [req.params.id, req.user.id], function (err) {
    if (err) return res.status(500).json({ message: 'Error al eliminar producto' });
    res.json({ success: true });
  });
});

module.exports = router; 