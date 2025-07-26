const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const dbPath = path.resolve(__dirname, '../../data.sqlite');
const db = new sqlite3.Database(dbPath);

// Crear tabla de productos si no existe (ahora con userId)
  db.run(`CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  categoria TEXT NOT NULL,
  descripcion TEXT NOT NULL,
  precio REAL NOT NULL,
  userId INTEGER NOT NULL
  )`);

// Crear tabla de categorías si no existe (ahora con userId)
  db.run(`CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  descripcion TEXT NOT NULL,
  userId INTEGER NOT NULL
  )`);

// Crear tabla de proveedores si no existe (ahora con userId)
  db.run(`CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  telefono TEXT NOT NULL,
  userId INTEGER NOT NULL
)`);

module.exports = db; 