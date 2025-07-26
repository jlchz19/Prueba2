import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProviderService {
  private apiUrl = `${environment.apiUrl}/api/proveedores`;

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  // Obtener todos los proveedores
  getProviders(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.getAuthHeaders() });
  }

  // Obtener un proveedor por ID
  getProvider(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  // Crear un nuevo proveedor
  createProvider(provider: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, provider, { headers: this.getAuthHeaders() });
  }

  // Actualizar un proveedor
  updateProvider(id: string, provider: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}`, provider, { headers: this.getAuthHeaders() });
  }

  // Eliminar un proveedor
  deleteProvider(id: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  // Obtener productos por proveedor
  getProductsByProvider(id: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${id}/productos`, { headers: this.getAuthHeaders() });
  }

  // Buscar proveedores
  searchProviders(query: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/search`, {
      params: { q: query },
      headers: this.getAuthHeaders()
    });
  }

  // Obtener estadísticas del proveedor
  getProviderStats(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}/stats`, { headers: this.getAuthHeaders() });
  }
} 