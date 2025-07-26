import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login',
  imports: [RouterModule, FormsModule, HttpClientModule, CommonModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  constructor(private router: Router, private authService: AuthService) {}

  showPassword = false;
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  rememberUser = false;

  // Cargar usuario guardado al inicializar
  ngOnInit() {
    const savedUser = localStorage.getItem('rememberedUser');
    if (savedUser) {
      this.rememberUser = true;
      const userInput = document.getElementById('username') as HTMLInputElement;
      if (userInput) {
        userInput.value = savedUser;
      }
    }
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  clearMessages() {
    this.errorMessage = '';
    this.successMessage = '';
  }

  validateForm(username: string, password: string): boolean {
    this.clearMessages();

    if (!username.trim()) {
      this.errorMessage = 'Por favor, ingresa tu nombre de usuario';
      return false;
    }

    if (!password) {
      this.errorMessage = 'Por favor, ingresa tu contraseña';
      return false;
    }

    if (password.length < 6) {
      this.errorMessage = 'La contraseña debe tener al menos 6 caracteres';
      return false;
    }

    return true;
  }

  onSubmit(event: Event) {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const username = (form.elements.namedItem('username') as HTMLInputElement).value.trim();
    const password = (form.elements.namedItem('password') as HTMLInputElement).value;

    if (!this.validateForm(username, password)) {
      return;
    }

    this.isLoading = true;
    this.clearMessages();

    // Guardar usuario si está marcada la opción
    if (this.rememberUser) {
      localStorage.setItem('rememberedUser', username);
    } else {
      localStorage.removeItem('rememberedUser');
    }

    this.authService.login(username, password).subscribe({
      next: () => {
        this.isLoading = false;
        this.successMessage = '¡Inicio de sesión exitoso! Redirigiendo...';
        
        // Redirigir después de mostrar el mensaje
        setTimeout(() => {
          this.router.navigate(['/dashboard']);
        }, 1500);
      },
      error: (err) => {
        this.isLoading = false;
        const errorMsg = err?.error?.message;
        
        if (errorMsg) {
          this.errorMessage = errorMsg;
        } else if (err.status === 401) {
          this.errorMessage = 'Usuario o contraseña incorrectos';
        } else if (err.status === 0 || err.status === 500) {
          this.errorMessage = 'Error de conexión. Verifica tu internet e inténtalo de nuevo.';
        } else {
          this.errorMessage = 'Error al iniciar sesión. Inténtalo de nuevo.';
        }
      }
    });
  }
}
