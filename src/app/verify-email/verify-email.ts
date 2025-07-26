import { Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-verify-email',
  imports: [RouterModule, FormsModule, HttpClientModule, CommonModule],
  templateUrl: './verify-email.html',
  styleUrl: './verify-email.css'
})
export class VerifyEmail {
  constructor(
    private router: Router, 
    private http: HttpClient,
    private route: ActivatedRoute
  ) {}

  verificationCode = '';
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  email = '';
  message = '';

  ngOnInit() {
    // Obtener parámetros de consulta
    this.route.queryParams.subscribe(params => {
      if (params['email']) {
        this.email = params['email'];
      } else {
    // Obtener el email del localStorage (guardado durante el registro)
    this.email = localStorage.getItem('pendingEmail') || '';
      }
      
      if (params['message']) {
        this.message = params['message'];
      }
      
    if (!this.email) {
      this.router.navigate(['/register']);
    }
    });
  }

  onSubmit(event: Event) {
    event.preventDefault();
    
    if (!this.verificationCode.trim()) {
      this.errorMessage = 'Por favor, ingresa el código de verificación';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

              this.http.post<any>(`${environment.apiUrl}/api/auth/verify-email`, {
            email: this.email,
            code: this.verificationCode
          })
    .subscribe({
      next: (res) => {
        this.isLoading = false;
        this.successMessage = '¡Email verificado exitosamente! Redirigiendo al login...';
        
        // Limpiar datos temporales
        localStorage.removeItem('pendingEmail');
        
        // Redirigir al login después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/']);
        }, 2000);
      },
      error: (err) => {
        this.isLoading = false;
        const errorMsg = err?.error?.message;
        
        if (errorMsg) {
          this.errorMessage = errorMsg;
        } else if (err.status === 400) {
          this.errorMessage = 'Código de verificación incorrecto';
        } else if (err.status === 404) {
          this.errorMessage = 'Email no encontrado o ya verificado';
        } else {
          this.errorMessage = 'Error al verificar el email. Inténtalo de nuevo.';
        }
      }
    });
  }

  resendCode() {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

              this.http.post<any>(`${environment.apiUrl}/api/auth/resend-code`, {
            email: this.email
          })
    .subscribe({
      next: (res) => {
        this.isLoading = false;
        this.successMessage = 'Nuevo código enviado a tu email';
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Error al reenviar el código. Inténtalo de nuevo.';
      }
    });
  }
} 