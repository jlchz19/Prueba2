import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = `${environment.apiUrl}/api/productos`;

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  // Obtener todos los productos
  getProducts(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.getAuthHeaders() });
  }

  // Obtener un producto por ID
  getProduct(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  // Crear un nuevo producto
  createProduct(product: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, product, { headers: this.getAuthHeaders() });
  }

  // Actualizar un producto
  updateProduct(id: string, product: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}`, product, { headers: this.getAuthHeaders() });
  }

  // Eliminar un producto
  deleteProduct(id: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  // Buscar productos
  searchProducts(query: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/search`, {
      params: { q: query },
      headers: this.getAuthHeaders()
    });
  }
} 