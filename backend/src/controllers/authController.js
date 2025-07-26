const jwt = require('jsonwebtoken');
const User = require('../models/user');
const crypto = require('crypto');
const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

// Guardar códigos de recuperación en memoria (en producción usar Redis)
const resetCodes = {};

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER || 'joseluischirinos380@gmail.com',
    pass: process.env.EMAIL_PASS || 'lxrs vjdh jpha kzek'
  }
});

// Verificar la conexión del transporter
transporter.verify(function(error, success) {
  if (error) {
    console.error('Error al configurar el servicio de email:', error);
  } else {
    console.log('Servidor de email listo para enviar mensajes');
  }
});

const JWT_SECRET = process.env.JWT_SECRET || 'supersecreto';

// Guardar tokens temporales en memoria (en producción usar base de datos o Redis)
const verificationCodes = {};

// Cargar template de email
const emailTemplate = fs.readFileSync(path.join(__dirname, '../../email-template-simple.html'), 'utf8');

// Función para generar código de verificación
function generateVerificationCode() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

// Función para enviar email de verificación
function sendVerificationEmail(email, code, name) {
  const emailContent = emailTemplate
    .replace('{{VERIFICATION_CODE}}', code)
    .replace('{{USER_NAME}}', name || 'Usuario');

  const mailOptions = {
    to: email,
    from: 'joseluischirinos380@gmail.com',
    subject: 'Gracias por registrarte al sistema de inventario',
    html: emailContent
  };

  return transporter.sendMail(mailOptions);
}

// Función para enviar email de recuperación de contraseña
function sendResetEmail(email, code, name) {
  const mailOptions = {
    to: email,
    from: 'joseluischirinos380@gmail.com',
    subject: '🔒 Recuperación de contraseña - Sistema de Inventario',
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 2px 8px #eee; padding: 32px 24px;">
        <div style="text-align:center; font-size: 48px; margin-bottom: 12px;">🔑</div>
        <h2 style="color: #4F46E5; text-align:center; margin-bottom: 8px;">Recuperación de contraseña</h2>
        <p style="color: #222; text-align:center;">Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
        <p style="color: #222; text-align:center;">Tu código de verificación es:</p>
        <div style="text-align:center; font-size: 2rem; font-weight: bold; letter-spacing: 4px; color: #4F46E5; margin: 12px 0 24px 0;">${code}</div>
        <p style="color: #888; font-size: 0.95rem; text-align:center;">Si no solicitaste este cambio, puedes ignorar este correo.</p>
        <div style="text-align:center; font-size: 32px; margin-top: 16px;">🔒</div>
      </div>
    `
  };

  return transporter.sendMail(mailOptions);
}

exports.register = (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) {
    return res.status(400).json({ message: 'Todos los campos son obligatorios' });
  }
  if (!/^[A-Za-z ]+$/.test(name)) {
    return res.status(400).json({ message: 'El nombre solo puede contener letras' });
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return res.status(400).json({ message: 'Correo electrónico no válido' });
  }
  if (password.length < 6) {
    return res.status(400).json({ message: 'La contraseña debe tener al menos 6 caracteres' });
  }
  
  User.findByName(name, (err, user) => {
    if (user) {
      return res.status(409).json({ message: 'El usuario ya existe' });
    }
    User.findByEmail(email, (err, userByEmail) => {
      if (userByEmail) {
        return res.status(409).json({ message: 'El email ya está registrado' });
      }
      
      // Crear usuario con estado no verificado
      User.createUser(name, email, password, 'user', false, (err, newUser) => {
        if (err) return res.status(500).json({ message: 'Error al registrar usuario' });
        
        // Generar código de verificación
        const verificationCode = generateVerificationCode();
        verificationCodes[email] = {
          code: verificationCode,
          userId: newUser.id,
          expires: Date.now() + 15 * 60 * 1000 // 15 minutos
        };
        
        // Enviar email de verificación
        console.log('Enviando email de verificación a:', email);
        console.log('Código de verificación:', verificationCode);
        
        sendVerificationEmail(email, verificationCode, name)
          .then(() => {
            console.log('Email de verificación enviado correctamente');
            return res.status(201).json({ 
              message: 'Usuario registrado correctamente. Verifica tu email para continuar.',
              requiresVerification: true
            });
          })
          .catch((error) => {
            console.error('Error enviando email:', error);
            // Intentar obtener más detalles del error
            if (error.response) {
              console.error('Detalles del error:', error.response.body);
            }
            return res.status(201).json({ 
              message: 'Usuario registrado correctamente. Verifica tu email para continuar.',
              requiresVerification: true
            });
          });
      });
    });
  });
};

// Verificar email con código
exports.verifyEmail = (req, res) => {
  const { email, code } = req.body;
  
  if (!email || !code) {
    return res.status(400).json({ message: 'Email y código de verificación requeridos' });
  }
  
  const verificationData = verificationCodes[email];
  
  if (!verificationData) {
    return res.status(404).json({ message: 'Email no encontrado o ya verificado' });
  }
  
  if (verificationData.expires < Date.now()) {
    delete verificationCodes[email];
    return res.status(400).json({ message: 'Código de verificación expirado' });
  }
  
  if (verificationData.code !== code) {
    return res.status(400).json({ message: 'Código de verificación incorrecto' });
  }
  
  // Marcar usuario como verificado
  User.verifyUser(verificationData.userId, (err) => {
    if (err) {
      return res.status(500).json({ message: 'Error al verificar usuario' });
    }
    
    // Eliminar código usado
    delete verificationCodes[email];
    
    return res.json({ 
      message: 'Email verificado exitosamente. Ya puedes iniciar sesión.',
      verified: true
    });
  });
};

// Reenviar código de verificación
exports.resendCode = (req, res) => {
  const { email } = req.body;
  
  if (!email) {
    return res.status(400).json({ message: 'Email requerido' });
  }
  
  User.findByEmail(email, (err, user) => {
    if (err || !user) {
      return res.status(404).json({ message: 'Email no encontrado' });
    }
    
    if (user.verified) {
      return res.status(400).json({ message: 'El email ya está verificado' });
    }
    
    // Generar nuevo código
    const verificationCode = generateVerificationCode();
    verificationCodes[email] = {
      code: verificationCode,
      userId: user.id,
      expires: Date.now() + 15 * 60 * 1000 // 15 minutos
    };
    
    // Enviar nuevo email
    sendVerificationEmail(email, verificationCode, user.name)
      .then(() => {
        return res.json({ 
          message: 'Nuevo código de verificación enviado',
          resent: true
        });
      })
      .catch((error) => {
        console.error('Error enviando email:', error);
        return res.status(500).json({ message: 'Error al reenviar código' });
      });
  });
};

exports.login = (req, res) => {
  const { name, password } = req.body;
  if (!name || !password) {
    return res.status(400).json({ message: 'Usuario y contraseña requeridos' });
  }
  User.findByName(name, (err, user) => {
    if (err || !user) {
      return res.status(401).json({ message: 'Usuario o contraseña incorrectos' });
    }
    
    // Verificar si el email está verificado
    if (!user.verified) {
      return res.status(401).json({ 
        message: 'Debes verificar tu email antes de iniciar sesión',
        requiresVerification: true
      });
    }
    
    User.validatePassword(user, password, (err, valid) => {
      if (err || !valid) {
        return res.status(401).json({ message: 'Usuario o contraseña incorrectos' });
      }
      // Generar JWT
      const token = jwt.sign({ id: user.id, name: user.name, role: user.role }, JWT_SECRET, { expiresIn: '2h' });
      return res.json({ token, role: user.role });
    });
  });
};

exports.updateUser = (req, res) => {
  const { id } = req.params;
  const { name, email, role } = req.body;
  if (!name || !email || !role) {
    return res.status(400).json({ message: 'Todos los campos son obligatorios' });
  }
  User.updateUser(id, name, email, role, (err, updated) => {
    if (err) return res.status(500).json({ message: 'Error al actualizar usuario' });
    res.json({ message: 'Usuario actualizado', user: updated });
  });
};

exports.deleteUser = (req, res) => {
  const { id } = req.params;
  User.deleteUser(id, (err) => {
    if (err) return res.status(500).json({ message: 'Error al eliminar usuario' });
    res.json({ message: 'Usuario eliminado' });
  });
}; 

// Solicitar código de recuperación
exports.forgot = (req, res) => {
  const { email } = req.body;
  
  if (!email) {
    return res.status(400).json({ message: 'Email requerido' });
  }

  User.findByEmail(email, (err, user) => {
    if (err || !user) {
      return res.status(404).json({ message: 'Email no encontrado' });
    }

    // Generar código de 6 dígitos
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    
    // Guardar código con tiempo de expiración (15 minutos)
    resetCodes[email] = {
      code,
      expires: Date.now() + 15 * 60 * 1000
    };

    // Enviar email con el código
    sendResetEmail(email, code, user.name)
      .then(() => {
        res.json({ message: 'Código de recuperación enviado' });
      })
      .catch((error) => {
        console.error('Error enviando email:', error);
        res.status(500).json({ message: 'Error al enviar el código' });
      });
  });
};

// Restablecer contraseña con código
exports.reset = (req, res) => {
  const { email, code, password } = req.body;

  if (!email || !code || !password) {
    return res.status(400).json({ message: 'Email, código y nueva contraseña son requeridos' });
  }

  const resetData = resetCodes[email];
  
  if (!resetData) {
    return res.status(404).json({ message: 'No hay solicitud de recuperación activa' });
  }

  if (resetData.expires < Date.now()) {
    delete resetCodes[email];
    return res.status(400).json({ message: 'El código ha expirado' });
  }

  if (resetData.code !== code) {
    return res.status(400).json({ message: 'Código incorrecto' });
  }

  // Buscar usuario por email
  User.findByEmail(email, (err, user) => {
    if (err || !user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    // Actualizar contraseña
    User.updatePassword(user.id, password, (err) => {
      if (err) {
        return res.status(500).json({ message: 'Error al actualizar contraseña' });
      }

      // Eliminar código usado
      delete resetCodes[email];

      res.json({ message: 'Contraseña actualizada correctamente' });
    });
  });
}; 