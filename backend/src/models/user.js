const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');
const path = require('path');

const dbPath = path.resolve(__dirname, '../../data.sqlite');
const db = new sqlite3.Database(dbPath);

// Crear tabla de usuarios si no existe
const init = () => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    verified INTEGER DEFAULT 0
  )`);
  
  // Agregar columna verified si no existe (para compatibilidad con bases de datos existentes)
  db.all("PRAGMA table_info(users)", (err, rows) => {
    if (err) {
      console.log('Error al verificar estructura de tabla:', err);
      return;
    }
    
    if (rows && rows.length > 0) {
      const hasVerifiedColumn = rows.some(row => row.name === 'verified');
      if (!hasVerifiedColumn) {
        db.run('ALTER TABLE users ADD COLUMN verified INTEGER DEFAULT 0', (err) => {
          if (err) {
            console.log('Columna verified ya existe o no se pudo agregar:', err.message);
          } else {
            console.log('Columna verified agregada exitosamente');
          }
        });
      }
    }
  });
};

init();

exports.createUser = (name, email, password, role = 'user', verified = false, cb) => {
  bcrypt.hash(password, 10, (err, hash) => {
    if (err) {
      console.error('Error al hashear contraseña:', err);
      return cb(err);
    }
    db.run(
      'INSERT INTO users (name, email, password, role, verified) VALUES (?, ?, ?, ?, ?)',
      [name, email, hash, role, verified ? 1 : 0],
      function (err) {
        if (err) {
          console.error('Error al insertar usuario:', err);
          return cb(err);
        }
        cb(null, { id: this.lastID, name, email, role, verified });
      }
    );
  });
};

exports.findByName = (name, cb) => {
  db.get('SELECT * FROM users WHERE name = ?', [name], (err, row) => {
    if (row) {
      row.verified = Boolean(row.verified);
    }
    cb(err, row);
  });
};

exports.findByEmail = (email, cb) => {
  db.get('SELECT * FROM users WHERE LOWER(email) = LOWER(?)', [email.trim()], (err, row) => {
    if (row) {
      row.verified = Boolean(row.verified);
    }
    cb(err, row);
  });
};

exports.validatePassword = (user, password, cb) => {
  bcrypt.compare(password, user.password, (err, same) => {
    cb(err, same);
  });
};

exports.getAllUsers = (cb) => {
  db.all('SELECT id, name, email, role, verified FROM users', [], (err, rows) => {
    if (rows) {
      rows.forEach(row => {
        row.verified = Boolean(row.verified);
      });
    }
    cb(err, rows);
  });
};

exports.updateUser = (id, name, email, role, cb) => {
  db.run(
    'UPDATE users SET name = ?, email = ?, role = ? WHERE id = ?',
    [name, email, role, id],
    function (err) {
      if (err) return cb(err);
      cb(null, { id, name, email, role });
    }
  );
};

exports.deleteUser = (id, cb) => {
  db.run('DELETE FROM users WHERE id = ?', [id], function (err) {
    if (err) return cb(err);
    cb(null, { id });
  });
};

exports.findById = (id, cb) => {
  db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
    if (row) {
      row.verified = Boolean(row.verified);
    }
    cb(err, row);
  });
};

exports.updatePassword = (id, password, cb) => {
  bcrypt.hash(password, 10, (err, hash) => {
    if (err) return cb(err);
    db.run('UPDATE users SET password = ? WHERE id = ?', [hash, id], function (err) {
      cb(err);
    });
  });
};

// Verificar usuario (marcar como verificado)
exports.verifyUser = (id, cb) => {
  db.run('UPDATE users SET verified = 1 WHERE id = ?', [id], function (err) {
    if (err) return cb(err);
    cb(null, { id, verified: true });
  });
};

// Obtener usuario por ID con información de verificación
exports.getUserById = (id, cb) => {
  db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
    if (row) {
      row.verified = Boolean(row.verified);
    }
    cb(err, row);
  });
};

// Contar usuarios
exports.countUsers = (cb) => {
  db.get('SELECT COUNT(*) as count FROM users', (err, row) => {
    if (err) return cb(err);
    cb(null, row ? row.count : 0);
  });
}; 