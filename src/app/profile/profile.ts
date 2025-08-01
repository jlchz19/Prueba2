import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Router } from '@angular/router';

// Componente de perfil mejorado con mejor manejo de errores y logging
@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {
  user = {
    id: 0,
    name: '',
    email: ''
  };
  
  isEditing = false;
  isLoading = false;
  message = '';
  messageType = '';

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    this.loadUserProfile();
  }

  loadUserProfile() {
    const token = localStorage.getItem('token');
    if (!token) {
      this.showMessage('No hay token de autenticación', 'error');
      this.router.navigate(['/login']);
      return;
    }

    console.log('Token:', token); // Para depuración
    console.log('URL:', `${environment.apiUrl}/api/auth/profile`); // Para depuración

    this.http.get<any>(`${environment.apiUrl}/api/auth/profile`, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }).subscribe({
      next: (data) => {
        console.log('Datos del perfil recibidos:', data);
        if (data) {
          this.user = {
            id: data.id || 0,
            name: data.name || '',
            email: data.email || ''
          };
        } else {
          this.showMessage('No se recibieron datos del perfil', 'error');
        }
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error completo:', error);
        let errorMessage = 'Error al cargar el perfil';
        
        if (error.status === 401) {
          errorMessage = 'Sesión expirada o inválida';
          this.router.navigate(['/login']);
        } else if (error.status === 404) {
          errorMessage = 'No se encontró la información del perfil';
        } else if (error.status === 0) {
          errorMessage = 'No se pudo conectar con el servidor';
        }
        
        this.showMessage(errorMessage, 'error');
      }
    });
  }

  updateProfile() {
    if (!this.user.name.trim() || !this.user.email.trim()) {
      this.showMessage('Por favor completa todos los campos', 'error');
      return;
    }

    this.isLoading = true;
    const token = localStorage.getItem('token');
    
    if (!token) {
      this.showMessage('No hay token de autenticación', 'error');
      this.router.navigate(['/login']);
      return;
    }

    this.http.put<any>(`${environment.apiUrl}/api/auth/profile`, this.user, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }).subscribe({
      next: (data) => {
        console.log('Perfil actualizado:', data);
        this.showMessage('Perfil actualizado exitosamente', 'success');
        this.isEditing = false;
        this.isLoading = false;
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error actualizando perfil:', error);
        let errorMessage = 'Error al actualizar el perfil';
        
        if (error.status === 401) {
          errorMessage = 'Sesión expirada o inválida';
          this.router.navigate(['/login']);
        } else if (error.status === 400) {
          errorMessage = 'Datos inválidos';
        }
        
        this.showMessage(errorMessage, 'error');
        this.isLoading = false;
      }
    });
  }

  toggleEdit() {
    this.isEditing = !this.isEditing;
  }

  showMessage(message: string, type: 'success' | 'error') {
    this.message = message;
    this.messageType = type;
    setTimeout(() => {
      this.message = '';
      this.messageType = '';
    }, 3000);
  }

  goBack() {
    this.router.navigate(['/dashboard']);
  }

  getCurrentDate(): string {
    return new Date().toLocaleDateString('es-ES');
  }
} 