import { Component } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { AuthService } from './services/auth.service';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {
  constructor(private router: Router, private authService: AuthService) {
    // DEBUG: Verificar configuración del API al iniciar la aplicación
    console.log('🚀 APP INICIADA');
    console.log('🔧 API URL:', environment.apiUrl);
    console.log('🔧 Version:', environment.version);
    console.log('🔧 Backend Render:', 'https://prueba1-5jnd.onrender.com');
    console.log('✅ Configuración verificada');
  }
} 