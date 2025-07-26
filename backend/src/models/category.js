const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, '../../data.sqlite');
const db = new sqlite3.Database(dbPath);

// Crear tabla de categorías si no existe
const init = () => {
  db.run(`CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    user_id INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
};

init();

// Contar categorías por usuario
exports.countCategories = (userId, cb) => {
  db.get('SELECT COUNT(*) as count FROM categories WHERE user_id = ?', [userId], (err, row) => {
    if (err) return cb(err);
    cb(null, row ? row.count : 0);
  });
};

// Obtener todas las categorías por usuario
exports.getAllCategories = (userId, cb) => {
  db.all('SELECT * FROM categories WHERE user_id = ? ORDER BY created_at DESC', [userId], (err, rows) => {
    cb(err, rows);
  });
};

// Crear categoría
exports.createCategory = (categoryData, userId, cb) => {
  const { name, description } = categoryData;
  db.run(
    'INSERT INTO categories (name, description, user_id) VALUES (?, ?, ?)',
    [name, description, userId],
    function (err) {
      if (err) return cb(err);
      cb(null, { id: this.lastID, ...categoryData });
    }
  );
};

// Actualizar categoría
exports.updateCategory = (id, categoryData, userId, cb) => {
  const { name, description } = categoryData;
  db.run(
    'UPDATE categories SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
    [name, description, id, userId],
    function (err) {
      if (err) return cb(err);
      cb(null, { id, ...categoryData });
    }
  );
};

// Eliminar categoría
exports.deleteCategory = (id, userId, cb) => {
  db.run('DELETE FROM categories WHERE id = ? AND user_id = ?', [id, userId], function (err) {
    if (err) return cb(err);
    cb(null, { id });
  });
};

// Obtener categoría por ID
exports.getCategoryById = (id, userId, cb) => {
  db.get('SELECT * FROM categories WHERE id = ? AND user_id = ?', [id, userId], (err, row) => {
    cb(err, row);
  });
}; 