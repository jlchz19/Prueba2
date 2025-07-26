import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-register',
  imports: [RouterModule, FormsModule, HttpClientModule, CommonModule],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  constructor(private router: Router, private http: HttpClient) {}

  showPassword = false;
  showConfirmPassword = false;
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  passwordStrength = 0;
  passwordStrengthText = '';
  passwordStrengthColor = '';
  attempts = 0;
  maxAttempts = 5;
  isBlocked = false;
  blockTime = 0;

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  toggleConfirmPasswordVisibility() {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  clearMessages() {
    this.errorMessage = '';
    this.successMessage = '';
  }

  // Sanitizar datos de entrada
  sanitizeInput(input: string): string {
    return input
      .trim()
      .replace(/[<>]/g, '') // Prevenir XSS básico
      .replace(/javascript:/gi, '') // Prevenir inyección de JavaScript
      .replace(/on\w+=/gi, ''); // Prevenir eventos maliciosos
  }

  // Validar fortaleza de contraseña
  validatePasswordStrength(password: string): { strength: number, text: string, color: string } {
    let score = 0;
    let feedback = '';

    if (password.length >= 8) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    if (score <= 1) {
      feedback = 'Muy débil';
      return { strength: score, text: feedback, color: '#dc2626' };
    } else if (score <= 2) {
      feedback = 'Débil';
      return { strength: score, text: feedback, color: '#ea580c' };
    } else if (score <= 3) {
      feedback = 'Media';
      return { strength: score, text: feedback, color: '#ca8a04' };
    } else if (score <= 4) {
      feedback = 'Fuerte';
      return { strength: score, text: feedback, color: '#16a34a' };
    } else {
      feedback = 'Muy fuerte';
      return { strength: score, text: feedback, color: '#059669' };
    }
  }

  // Actualizar fortaleza de contraseña en tiempo real
  onPasswordChange(event: Event) {
    const password = (event.target as HTMLInputElement).value;
    const strength = this.validatePasswordStrength(password);
    this.passwordStrength = strength.strength;
    this.passwordStrengthText = strength.text;
    this.passwordStrengthColor = strength.color;
  }

  // Verificar si el usuario está bloqueado
  checkIfBlocked(): boolean {
    const lastAttempt = localStorage.getItem('lastRegisterAttempt');
    const attempts = parseInt(localStorage.getItem('registerAttempts') || '0');
    
    if (lastAttempt && attempts >= this.maxAttempts) {
      const timeDiff = Date.now() - parseInt(lastAttempt);
      const blockDuration = 15 * 60 * 1000; // 15 minutos
      
      if (timeDiff < blockDuration) {
        this.isBlocked = true;
        this.blockTime = Math.ceil((blockDuration - timeDiff) / 1000 / 60);
        return true;
      } else {
        // Resetear intentos después del bloqueo
        localStorage.removeItem('registerAttempts');
        localStorage.removeItem('lastRegisterAttempt');
        this.isBlocked = false;
        this.attempts = 0;
      }
    }
    return false;
  }

  // Registrar intento fallido
  recordFailedAttempt() {
    this.attempts++;
    localStorage.setItem('registerAttempts', this.attempts.toString());
    localStorage.setItem('lastRegisterAttempt', Date.now().toString());
    
    if (this.attempts >= this.maxAttempts) {
      this.isBlocked = true;
      this.blockTime = 15;
    }
  }

  // Validar formato de email más estricto
  validateEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  // Validar nombre más estricto
  validateName(name: string): boolean {
    // Solo letras, espacios y algunos caracteres especiales comunes
    const nameRegex = /^[A-Za-zÀ-ÿ\s'-]{2,50}$/;
    return nameRegex.test(name);
  }

  validateForm(name: string, email: string, password: string, confirmPassword: string): boolean {
    this.clearMessages();

    // Verificar si está bloqueado
    if (this.checkIfBlocked()) {
      this.errorMessage = `Demasiados intentos fallidos. Inténtalo de nuevo en ${this.blockTime} minutos.`;
      return false;
    }

    // Validaciones básicas
    if (!name || !email || !password || !confirmPassword) {
      this.errorMessage = 'Por favor, completa todos los campos';
      return false;
    }

    // Sanitizar entradas
    const sanitizedName = this.sanitizeInput(name);
    const sanitizedEmail = this.sanitizeInput(email);

    // Validar nombre
    if (!this.validateName(sanitizedName)) {
      this.errorMessage = 'El nombre solo puede contener letras, espacios y algunos caracteres especiales (2-50 caracteres)';
      return false;
    }

    // Validar email
    if (!this.validateEmail(sanitizedEmail)) {
      this.errorMessage = 'Correo electrónico no válido';
      return false;
    }

    // Validar contraseña
    if (password.length < 8) {
      this.errorMessage = 'La contraseña debe tener al menos 8 caracteres';
      return false;
    }

    // Verificar fortaleza de contraseña
    const strength = this.validatePasswordStrength(password);
    if (strength.strength <= 2) {
      this.errorMessage = 'La contraseña es muy débil. Usa mayúsculas, minúsculas, números y símbolos.';
      return false;
    }

    if (password !== confirmPassword) {
      this.errorMessage = 'Las contraseñas no coinciden';
      return false;
    }

    // Verificar contraseñas comunes
    const commonPasswords = ['password', '123456', 'qwerty', 'admin', 'user'];
    if (commonPasswords.includes(password.toLowerCase())) {
      this.errorMessage = 'No uses contraseñas comunes. Elige una contraseña más segura.';
      return false;
    }

    return true;
  }

  onSubmit(event: Event) {
    event.preventDefault();
    
    console.log('Iniciando proceso de registro...');
    
    // Verificar bloqueo
    if (this.checkIfBlocked()) {
      this.errorMessage = `Demasiados intentos fallidos. Inténtalo de nuevo en ${this.blockTime} minutos.`;
      console.log('Usuario bloqueado');
      return;
    }

    const form = event.target as HTMLFormElement;
    const name = this.sanitizeInput((form.elements.namedItem('username') as HTMLInputElement).value);
    const email = this.sanitizeInput((form.elements.namedItem('email') as HTMLInputElement).value);
    const password = (form.elements.namedItem('password') as HTMLInputElement).value;
    const confirmPassword = (form.elements.namedItem('confirmPassword') as HTMLInputElement).value;

    console.log('Datos del formulario:', { name, email, password: '***', confirmPassword: '***' });

    if (!this.validateForm(name, email, password, confirmPassword)) {
      console.log('Validación fallida:', this.errorMessage);
      return;
    }

    this.isLoading = true;
    this.clearMessages();

    const userData = { name, email, password };
    console.log('Enviando datos al backend:', { ...userData, password: '***' });

    // Enviar al backend
    this.http.post<any>(`${environment.apiUrl}/api/auth/register`, userData)
      .subscribe({
        next: (res) => {
          console.log('Respuesta exitosa del backend:', res);
          this.isLoading = false;
          // Limpiar intentos fallidos en caso de éxito
          localStorage.removeItem('registerAttempts');
          localStorage.removeItem('lastRegisterAttempt');
          
          // Guardar el email para la verificación
          localStorage.setItem('pendingEmail', email);
          
          this.successMessage = res?.message || '¡Registro exitoso! Verifica tu email para continuar.';
          
          // Redirigir a la verificación de email después de mostrar el mensaje
          setTimeout(() => {
            this.router.navigate(['/verify-email']);
          }, 2000);
        },
        error: (err) => {
          console.error('Error en el registro:', err);
          this.isLoading = false;
          this.recordFailedAttempt();
          
          const errorMsg = err?.error?.message;
          
          if (errorMsg) {
            this.errorMessage = errorMsg;
          } else if (err.status === 409) {
            this.errorMessage = 'El usuario o correo ya existe';
          } else if (err.status === 0 || err.status === 500) {
            this.errorMessage = 'Error de conexión. Verifica tu internet e inténtalo de nuevo.';
          } else {
            this.errorMessage = 'Error al registrar usuario. Inténtalo de nuevo.';
          }
        }
      });
  }
}
