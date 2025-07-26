const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, '../../data.sqlite');
const db = new sqlite3.Database(dbPath);

// Crear tabla de productos si no existe
const init = () => {
  db.run(`CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER DEFAULT 0,
    category_id INTEGER,
    provider_id INTEGER,
    user_id INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
};

init();

// Contar productos por usuario
exports.countProducts = (userId, cb) => {
  db.get('SELECT COUNT(*) as count FROM products WHERE user_id = ?', [userId], (err, row) => {
    if (err) return cb(err);
    cb(null, row ? row.count : 0);
  });
};

// Obtener todos los productos por usuario
exports.getAllProducts = (userId, cb) => {
  db.all('SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC', [userId], (err, rows) => {
    cb(err, rows);
  });
};

// Crear producto
exports.createProduct = (productData, userId, cb) => {
  const { name, description, price, stock, category_id, provider_id } = productData;
  db.run(
    'INSERT INTO products (name, description, price, stock, category_id, provider_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
    [name, description, price, stock, category_id, provider_id, userId],
    function (err) {
      if (err) return cb(err);
      cb(null, { id: this.lastID, ...productData });
    }
  );
};

// Actualizar producto
exports.updateProduct = (id, productData, userId, cb) => {
  const { name, description, price, stock, category_id, provider_id } = productData;
  db.run(
    'UPDATE products SET name = ?, description = ?, price = ?, stock = ?, category_id = ?, provider_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
    [name, description, price, stock, category_id, provider_id, id, userId],
    function (err) {
      if (err) return cb(err);
      cb(null, { id, ...productData });
    }
  );
};

// Eliminar producto
exports.deleteProduct = (id, userId, cb) => {
  db.run('DELETE FROM products WHERE id = ? AND user_id = ?', [id, userId], function (err) {
    if (err) return cb(err);
    cb(null, { id });
  });
};

// Obtener producto por ID
exports.getProductById = (id, userId, cb) => {
  db.get('SELECT * FROM products WHERE id = ? AND user_id = ?', [id, userId], (err, row) => {
    cb(err, row);
  });
}; 