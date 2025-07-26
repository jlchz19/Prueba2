import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private apiUrl = `${environment.apiUrl}/api/categorias`;

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  // Obtener todas las categorías
  getCategories(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.getAuthHeaders() });
  }

  // Obtener una categoría por ID
  getCategory(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  // Crear una nueva categoría
  createCategory(category: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, category, { headers: this.getAuthHeaders() });
  }

  // Actualizar una categoría
  updateCategory(id: string, category: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}`, category, { headers: this.getAuthHeaders() });
  }

  // Eliminar una categoría
  deleteCategory(id: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  // Obtener productos por categoría
  getProductsByCategory(id: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${id}/productos`, { headers: this.getAuthHeaders() });
  }

  // Buscar categorías
  searchCategories(query: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/search`, {
      params: { q: query },
      headers: this.getAuthHeaders()
    });
  }
} 