import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Router } from '@angular/router';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, FormsModule],
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
    if (token) {
      this.http.get<any>(`${environment.apiUrl}/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      }).subscribe({
        next: (data) => {
          this.user = {
            ...data
          };
        },
        error: (error) => {
          console.error('Error cargando perfil:', error);
          this.showMessage('Error al cargar el perfil', 'error');
        }
      });
    }
  }

  toggleEdit() {
    this.isEditing = !this.isEditing;
    if (!this.isEditing) {
      this.loadUserProfile(); // Recargar datos originales
    }
  }

  updateProfile() {
    if (!this.user.name.trim() || !this.user.email.trim()) {
      this.showMessage('Por favor completa todos los campos', 'error');
      return;
    }

    this.isLoading = true;
    const token = localStorage.getItem('token');
    
    this.http.put<any>(`${environment.apiUrl}/profile`, {
      name: this.user.name,
      email: this.user.email
    }, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        this.showMessage('Perfil actualizado correctamente', 'success');
        this.isEditing = false;
        this.isLoading = false;
        // Actualizar localStorage
        localStorage.setItem('username', this.user.name);
      },
      error: (error) => {
        this.showMessage('Error al actualizar el perfil', 'error');
        this.isLoading = false;
      }
    });
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