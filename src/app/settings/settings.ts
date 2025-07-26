import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { TranslationService } from '../services/translation.service';
import { SharedModule } from '../shared';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-settings',
  imports: [CommonModule, FormsModule, SharedModule],
  templateUrl: './settings.html',
  styleUrl: './settings.css'
})
export class Settings implements OnInit {
  settings = {
    appearance: {
      theme: 'light',
      language: 'es',
      fontSize: 'medium'
    }
  };

  isLoading = false;
  message = '';
  messageType = '';

  constructor(
    private http: HttpClient, 
    private router: Router,
    public translationService: TranslationService
  ) {}

  ngOnInit() {
    this.loadSettings();
    this.loadStoredSettings();
  }

  loadStoredSettings() {
    const storedSettings = localStorage.getItem('appSettings');
    if (storedSettings) {
      try {
        const settings = JSON.parse(storedSettings);
        this.settings = { ...this.settings, ...settings };
        this.applySettings();
        console.log('✅ Configuración cargada desde localStorage');
      } catch (error) {
        console.error('Error cargando configuración guardada:', error);
      }
    } else {
      console.log('📝 No hay configuración guardada, usando valores por defecto');
      this.applySettings();
    }
    
    // Cargar idioma guardado
    this.loadStoredLanguage();
  }

  loadStoredLanguage() {
    const storedLanguage = localStorage.getItem('appLanguage');
    if (storedLanguage) {
      this.settings.appearance.language = storedLanguage;
      this.applyLanguage();
      console.log('✅ Idioma cargado desde localStorage:', storedLanguage);
    } else {
      console.log('📝 No hay idioma guardado, usando español por defecto');
      this.applyLanguage();
    }
  }

  loadSettings() {
    const token = localStorage.getItem('token');
    if (token) {
      this.http.get<any>(`${environment.apiUrl}/settings`, {
        headers: { Authorization: `Bearer ${token}` }
      }).subscribe({
        next: (data) => {
          this.settings = { ...this.settings, ...data };
          this.applySettings();
        },
        error: (error) => {
          console.error('Error cargando configuración:', error);
          // Usar configuración por defecto
        }
      });
    }
  }

  updateSettings() {
    this.isLoading = true;
    const token = localStorage.getItem('token');
    
    // Aplicar cambios inmediatamente
    this.applySettings();
    
    this.http.put<any>(`${environment.apiUrl}/settings`, this.settings, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (data) => {
        this.showMessage('Configuración guardada correctamente', 'success');
        this.isLoading = false;
      },
      error: (error) => {
        this.showMessage('Error al guardar la configuración', 'error');
        this.isLoading = false;
      }
    });
  }

  applySettings() {
    console.log('🔄 Aplicando configuración...');
    
    // Aplicar tema
    this.applyTheme();
    
    // Aplicar tamaño de fuente
    this.applyFontSize();
    
    // Aplicar idioma
    this.applyLanguage();
    
    // Guardar configuración en localStorage para persistencia
    localStorage.setItem('appSettings', JSON.stringify(this.settings));
    
    console.log('✅ Configuración aplicada y guardada');
  }

  applyTheme() {
    const theme = this.settings.appearance.theme;
    const body = document.body;
    
    console.log('🎨 Aplicando tema:', theme);
    
    // Remover clases de tema anteriores
    body.classList.remove('theme-light', 'theme-dark');
    
    // Aplicar nuevo tema
    if (theme === 'dark') {
      body.classList.add('theme-dark');
      console.log('✅ Tema oscuro aplicado');
    } else if (theme === 'light') {
      body.classList.add('theme-light');
      console.log('✅ Tema claro aplicado');
    } else if (theme === 'auto') {
      // Detectar preferencia del sistema
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
      console.log('✅ Tema automático aplicado:', prefersDark ? 'oscuro' : 'claro');
    }
    
    console.log('📋 Clases del body:', body.className);
  }

  applyFontSize() {
    const fontSize = this.settings.appearance.fontSize;
    const body = document.body;
    
    console.log('📝 Aplicando tamaño de fuente:', fontSize);
    
    // Remover clases de tamaño anteriores
    body.classList.remove('font-small', 'font-medium', 'font-large');
    
    // Aplicar nuevo tamaño
    body.classList.add(`font-${fontSize}`);
    
    console.log('✅ Tamaño de fuente aplicado:', `font-${fontSize}`);
    console.log('📋 Clases del body:', body.className);
  }

  // Métodos para aplicar cambios inmediatamente
  onThemeChange() {
    console.log('🔄 Cambio de tema detectado:', this.settings.appearance.theme);
    this.applyTheme();
  }

  onFontSizeChange() {
    console.log('🔄 Cambio de tamaño de fuente detectado:', this.settings.appearance.fontSize);
    this.applyFontSize();
  }

  async onLanguageChange() {
    const language = this.settings.appearance.language;
    console.log('🌐 Idioma cambiado a:', language);
    
    try {
      // Actualizar el servicio de traducciones
      this.translationService.setLanguage(language as 'es' | 'en');
      
      // Aplicar idioma inmediatamente
      this.applyLanguage();
      
      // Guardar en localStorage
      localStorage.setItem('appLanguage', language);
      
      // Guardar configuración en el backend
      await this.updateSettings();
      
      // Mostrar mensaje de confirmación
      const message = this.translationService.translate('language_changed');
      this.showMessage(message, 'success');
      
      // Recargar la página para aplicar traducciones
      setTimeout(() => {
        // Forzar recarga completa
        window.location.reload();
      }, 1000);
      
    } catch (error) {
      console.error('Error al cambiar el idioma:', error);
      this.showMessage('Error al cambiar el idioma', 'error');
    }
  }

  applyLanguage() {
    const language = this.settings.appearance.language;
    const html = document.documentElement;
    
    // Remover clases de idioma anteriores
    html.classList.remove('lang-es', 'lang-en');
    
    // Aplicar nuevo idioma
    html.classList.add(`lang-${language}`);
    
    console.log('✅ Idioma aplicado:', language);
    console.log('📋 Clases del html:', html.className);
  }

  resetSettings() {
    if (confirm('¿Estás seguro de que quieres restablecer toda la configuración?')) {
      this.settings = {
        appearance: {
          theme: 'light',
          language: 'es',
          fontSize: 'medium'
        }
      };
      this.applySettings();
      this.showMessage('Configuración restablecida', 'success');
    }
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
} 