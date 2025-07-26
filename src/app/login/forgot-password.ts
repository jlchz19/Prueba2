import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-forgot-password',
  imports: [RouterModule, FormsModule, HttpClientModule, CommonModule],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.css'
})
export class ForgotPassword {
  email = '';
  code = '';
  newPassword = '';
  confirmPassword = '';
  step = 1; // 1: email, 2: código, 3: nueva contraseña
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  showPassword = false;
  showConfirmPassword = false;

  constructor(private http: HttpClient, private router: Router) {}

  // Paso 1: Solicitar código de recuperación
  async requestCode() {
    if (!this.email) {
      this.errorMessage = 'Por favor, ingresa tu email';
      return;
    }

    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(this.email)) {
      this.errorMessage = 'Por favor, ingresa un email válido';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    try {
      await this.http.post(`${environment.apiUrl}/api/auth/forgot`, { email: this.email }).toPromise();
      this.successMessage = 'Se ha enviado un código de verificación a tu email';
      this.step = 2;
    } catch (error: any) {
      this.errorMessage = error.error?.message || 'Error al enviar el código de verificación';
    } finally {
      this.isLoading = false;
    }
  }

  // Paso 2: Verificar código y establecer nueva contraseña
  async resetPassword() {
    if (!this.code) {
      this.errorMessage = 'Por favor, ingresa el código de verificación';
      return;
    }

    if (!this.newPassword) {
      this.errorMessage = 'Por favor, ingresa la nueva contraseña';
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage = 'Las contraseñas no coinciden';
      return;
    }

    if (this.newPassword.length < 6) {
      this.errorMessage = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    try {
      await this.http.post(`${environment.apiUrl}/api/auth/reset`, {
        email: this.email,
        code: this.code,
        password: this.newPassword
      }).toPromise();

      this.successMessage = 'Contraseña restablecida correctamente';
      setTimeout(() => {
        this.router.navigate(['/']);
      }, 2000);
    } catch (error: any) {
      this.errorMessage = error.error?.message || 'Error al restablecer la contraseña';
    } finally {
      this.isLoading = false;
    }
  }

  // Solicitar nuevo código
  async resendCode() {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    try {
      await this.http.post(`${environment.apiUrl}/api/auth/forgot`, { email: this.email }).toPromise();
      this.successMessage = 'Se ha enviado un nuevo código de verificación';
    } catch (error: any) {
      this.errorMessage = error.error?.message || 'Error al reenviar el código';
    } finally {
      this.isLoading = false;
    }
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  toggleConfirmPasswordVisibility() {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  goBack() {
    if (this.step > 1) {
      this.step--;
      this.errorMessage = '';
      this.successMessage = '';
    } else {
      this.router.navigate(['/']);
    }
  }
} 