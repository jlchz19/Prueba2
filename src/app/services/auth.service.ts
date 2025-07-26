import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  private userSubject = new BehaviorSubject<any>(null);

  constructor(private http: HttpClient) {
    // Verificar si hay un token almacenado al iniciar el servicio
    const token = localStorage.getItem('token');
    if (token) {
      this.isAuthenticatedSubject.next(true);
      this.loadUserProfile();
    }
  }

  // Getters para los observables
  get isAuthenticated$() {
    return this.isAuthenticatedSubject.asObservable();
  }

  get user$() {
    return this.userSubject.asObservable();
  }

  // Headers comunes para las peticiones autenticadas
  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  // Login
  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/api/auth/login`, { name: username, password })
      .pipe(
        tap(response => {
          if (response && response.token) {
            localStorage.setItem('token', response.token);
            localStorage.setItem('username', username);
            this.isAuthenticatedSubject.next(true);
            this.loadUserProfile();
          }
        })
      );
  }

  // Registro
  register(userData: any): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/api/auth/register`, userData);
  }

  // Recuperación de contraseña
  forgotPassword(email: string): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/api/auth/forgot`, { email });
  }

  // Restablecer contraseña
  resetPassword(email: string, code: string, password: string): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/api/auth/reset`, { email, code, password });
  }

  // Verificar email
  verifyEmail(code: string): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/api/auth/verify-email`, { code });
  }

  // Reenviar código de verificación
  resendVerificationCode(email: string): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/api/auth/resend-code`, { email });
  }

  // Cargar perfil del usuario
  loadUserProfile(): void {
    if (this.isAuthenticatedSubject.value) {
      this.http.get<any>(`${environment.apiUrl}/api/auth/profile`, { headers: this.getAuthHeaders() })
        .subscribe({
          next: (user) => this.userSubject.next(user),
          error: (error) => {
            console.error('Error al cargar el perfil:', error);
            if (error.status === 401) {
              this.logout();
            }
          }
        });
    }
  }

  // Actualizar perfil
  updateProfile(profileData: any): Observable<any> {
    return this.http.put<any>(
      `${environment.apiUrl}/api/auth/profile`,
      profileData,
      { headers: this.getAuthHeaders() }
    );
  }

  // Cambiar contraseña
  changePassword(currentPassword: string, newPassword: string): Observable<any> {
    return this.http.put<any>(
      `${environment.apiUrl}/api/auth/change-password`,
      { currentPassword, newPassword },
      { headers: this.getAuthHeaders() }
    );
  }

  // Cerrar sesión
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    this.isAuthenticatedSubject.next(false);
    this.userSubject.next(null);
  }

  // Verificar si el token es válido
  isTokenValid(): boolean {
    const token = localStorage.getItem('token');
    if (!token) return false;

    try {
      const tokenData = JSON.parse(atob(token.split('.')[1]));
      const expirationDate = new Date(tokenData.exp * 1000);
      return expirationDate > new Date();
    } catch {
      return false;
    }
  }
} 