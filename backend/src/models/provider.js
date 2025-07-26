const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, '../../data.sqlite');
const db = new sqlite3.Database(dbPath);

// Crear tabla de proveedores si no existe
const init = () => {
  db.run(`CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    user_id INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
};

init();

// Contar proveedores por usuario
exports.countProviders = (userId, cb) => {
  db.get('SELECT COUNT(*) as count FROM providers WHERE user_id = ?', [userId], (err, row) => {
    if (err) return cb(err);
    cb(null, row ? row.count : 0);
  });
};

// Obtener todos los proveedores por usuario
exports.getAllProviders = (userId, cb) => {
  db.all('SELECT * FROM providers WHERE user_id = ? ORDER BY created_at DESC', [userId], (err, rows) => {
    cb(err, rows);
  });
};

// Crear proveedor
exports.createProvider = (providerData, userId, cb) => {
  const { name, email, phone, address } = providerData;
  db.run(
    'INSERT INTO providers (name, email, phone, address, user_id) VALUES (?, ?, ?, ?, ?)',
    [name, email, phone, address, userId],
    function (err) {
      if (err) return cb(err);
      cb(null, { id: this.lastID, ...providerData });
    }
  );
};

// Actualizar proveedor
exports.updateProvider = (id, providerData, userId, cb) => {
  const { name, email, phone, address } = providerData;
  db.run(
    'UPDATE providers SET name = ?, email = ?, phone = ?, address = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
    [name, email, phone, address, id, userId],
    function (err) {
      if (err) return cb(err);
      cb(null, { id, ...providerData });
    }
  );
};

// Eliminar proveedor
exports.deleteProvider = (id, userId, cb) => {
  db.run('DELETE FROM providers WHERE id = ? AND user_id = ?', [id, userId], function (err) {
    if (err) return cb(err);
    cb(null, { id });
  });
};

// Obtener proveedor por ID
exports.getProviderById = (id, userId, cb) => {
  db.get('SELECT * FROM providers WHERE id = ? AND user_id = ?', [id, userId], (err, row) => {
    cb(err, row);
  });
}; 