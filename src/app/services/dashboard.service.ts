import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Activity {
  id: number;
  type: 'product' | 'category' | 'provider';
  title: string;
  description: string;
  time: string;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = `${environment.apiUrl}/api/dashboard`;

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  // Obtener actividad reciente
  getRecentActivity(): Observable<Activity[]> {
    return this.http.get<Activity[]>(`${this.apiUrl}/activity`, {
      headers: this.getAuthHeaders()
    });
  }

  // Obtener estadísticas del dashboard
  getDashboardStats(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/stats`, {
      headers: this.getAuthHeaders()
    });
  }

  // Obtener notificaciones del usuario
  getUserNotifications(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/notifications`, {
      headers: this.getAuthHeaders()
    });
  }

  // Marcar notificación como leída
  markNotificationAsRead(notificationId: number): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/notifications/${notificationId}/read`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  // Obtener resumen de productos
  getProductsSummary(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/products/summary`, {
      headers: this.getAuthHeaders()
    });
  }

  // Obtener resumen de categorías
  getCategoriesSummary(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/categories/summary`, {
      headers: this.getAuthHeaders()
    });
  }

  // Obtener resumen de proveedores
  getProvidersSummary(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/providers/summary`, {
      headers: this.getAuthHeaders()
    });
  }
} 