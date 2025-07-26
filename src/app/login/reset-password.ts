import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reset-password.html',
  styleUrl: './reset-password.css'
})
export class ResetPassword implements OnInit {
  password = '';
  confirmPassword = '';
  message = '';
  loading = false;
  token = '';

  constructor(private route: ActivatedRoute, private http: HttpClient, private router: Router) {
    this.route.params.subscribe(params => {
      this.token = params['token'];
    });
  }

  ngOnInit(): void {
    // No specific initialization needed here as token is set in constructor
  }

  onSubmit(event: Event) {
    event.preventDefault();
    if (!this.password || !this.confirmPassword) {
      this.message = 'Por favor, completa ambos campos.';
      return;
    }
    if (this.password !== this.confirmPassword) {
      this.message = 'Las contraseñas no coinciden.';
      return;
    }
    this.loading = true;
    this.http.post<any>(`${environment.apiUrl}/reset`, { token: this.token, password: this.password })
      .subscribe({
        next: (res) => {
          this.message = res.message || 'Contraseña restablecida correctamente.';
          this.loading = false;
          setTimeout(() => this.router.navigate(['/login']), 2000);
        },
        error: (err) => {
          this.message = err?.error?.error || 'Error al restablecer la contraseña.';
          this.loading = false;
        }
      });
  }
} 