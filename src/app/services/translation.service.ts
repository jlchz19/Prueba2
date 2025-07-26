import { Injectable } from '@angular/core';

export interface Translation {
  [key: string]: {
    es: string;
    en: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class TranslationService {
  private currentLanguage = 'es';
  
  private translations: Translation = {
    // Dashboard
    'welcome_back': {
      es: '¡Bienvenido de vuelta, {{name}}!',
      en: 'Welcome back, {{name}}!'
    },
    'dashboard_subtitle': {
      es: 'Aquí tienes un resumen de tu sistema de inventario',
      en: 'Here you have a summary of your inventory system'
    },
    'session_started': {
      es: 'Sesión iniciada: {{date}}',
      en: 'Session started: {{date}}'
    },
    'my_profile': {
      es: 'Mi Perfil',
      en: 'My Profile'
    },
    'settings': {
      es: 'Configuración',
      en: 'Settings'
    },
    'logout': {
      es: 'Cerrar Sesión',
      en: 'Logout'
    },
    'quick_actions': {
      es: '⚡ Acciones Rápidas',
      en: '⚡ Quick Actions'
    },
    'add_product': {
      es: 'Agregar Producto',
      en: 'Add Product'
    },
    'new_category': {
      es: 'Nueva Categoría',
      en: 'New Category'
    },
    'add_provider': {
      es: 'Agregar Proveedor',
      en: 'Add Provider'
    },
    'recent_activity': {
      es: '📊 Actividad Reciente',
      en: '📊 Recent Activity'
    },
    'new_product_added': {
      es: 'Nuevo producto agregado',
      en: 'New product added'
    },
    'product_added_description': {
      es: 'Se agregó un producto al inventario',
      en: 'A product was added to inventory'
    },
    'category_updated': {
      es: 'Categoría actualizada',
      en: 'Category updated'
    },
    'category_updated_description': {
      es: 'Se modificó una categoría del sistema',
      en: 'A system category was modified'
    },
    'provider_registered': {
      es: 'Proveedor registrado',
      en: 'Provider registered'
    },
    'provider_registered_description': {
      es: 'Se agregó un nuevo proveedor',
      en: 'A new provider was added'
    },
    'ago_5_minutes': {
      es: 'Hace 5 minutos',
      en: '5 minutes ago'
    },
    'ago_15_minutes': {
      es: 'Hace 15 minutos',
      en: '15 minutes ago'
    },
    'ago_1_hour': {
      es: 'Hace 1 hora',
      en: '1 hour ago'
    },
    'ago_2_hours': {
      es: 'Hace 2 horas',
      en: '2 hours ago'
    },
    'welcome_message': {
      es: '¡Bienvenido al sistema!',
      en: 'Welcome to the system!'
    },
    'welcome_description': {
      es: 'Tu sesión se ha iniciado correctamente. Disfruta gestionando tu inventario.',
      en: 'Your session has started successfully. Enjoy managing your inventory.'
    },
    'closing_session': {
      es: 'Cerrando sesión',
      en: 'Closing session'
    },
    'logout_message': {
      es: 'Has cerrado sesión correctamente. ¡Hasta pronto!',
      en: 'You have logged out successfully. See you soon!'
    },
    'system_version': {
      es: '© 2024 Sistema de Inventario - Versión 2.0',
      en: '© 2024 Inventory System - Version 2.0'
    },
    'help': {
      es: 'Ayuda',
      en: 'Help'
    },
    'support': {
      es: 'Soporte',
      en: 'Support'
    },
    'documentation': {
      es: 'Documentación',
      en: 'Documentation'
    },

    // Settings
    'notifications': {
      es: '🔔 Notificaciones',
      en: '🔔 Notifications'
    },
    'email_notifications': {
      es: 'Notificaciones por Email',
      en: 'Email Notifications'
    },
    'email_notifications_desc': {
      es: 'Recibe notificaciones importantes por correo electrónico',
      en: 'Receive important notifications by email'
    },
    'push_notifications': {
      es: 'Notificaciones Push',
      en: 'Push Notifications'
    },
    'push_notifications_desc': {
      es: 'Recibe notificaciones en tiempo real en el navegador',
      en: 'Receive real-time notifications in the browser'
    },
    'system_notifications': {
      es: 'Notificaciones del Sistema',
      en: 'System Notifications'
    },
    'system_notifications_desc': {
      es: 'Muestra notificaciones dentro de la aplicación',
      en: 'Show notifications within the application'
    },
    'appearance': {
      es: '🎨 Apariencia',
      en: '🎨 Appearance'
    },
    'theme': {
      es: 'Tema',
      en: 'Theme'
    },
    'theme_desc': {
      es: 'Elige el tema visual de la aplicación',
      en: 'Choose the visual theme of the application'
    },
    'light': {
      es: 'Claro',
      en: 'Light'
    },
    'dark': {
      es: 'Oscuro',
      en: 'Dark'
    },
    'auto': {
      es: 'Automático',
      en: 'Auto'
    },
    'language': {
      es: 'Idioma',
      en: 'Language'
    },
    'language_desc': {
      es: 'Idioma de la interfaz',
      en: 'Interface language'
    },
    'spanish': {
      es: 'Español',
      en: 'Spanish'
    },
    'english': {
      es: 'English',
      en: 'English'
    },
    'font_size': {
      es: 'Tamaño de Fuente',
      en: 'Font Size'
    },
    'font_size_desc': {
      es: 'Tamaño del texto en la aplicación',
      en: 'Text size in the application'
    },
    'small': {
      es: 'Pequeño',
      en: 'Small'
    },
    'medium': {
      es: 'Mediano',
      en: 'Medium'
    },
    'large': {
      es: 'Grande',
      en: 'Large'
    },
    'security': {
      es: '🔒 Seguridad',
      en: '🔒 Security'
    },
    'two_factor': {
      es: 'Autenticación de Dos Factores',
      en: 'Two-Factor Authentication'
    },
    'two_factor_desc': {
      es: 'Agrega una capa extra de seguridad a tu cuenta',
      en: 'Add an extra layer of security to your account'
    },
    'session_timeout': {
      es: 'Tiempo de Sesión (minutos)',
      en: 'Session Timeout (minutes)'
    },
    'session_timeout_desc': {
      es: 'Tiempo antes de que la sesión expire automáticamente',
      en: 'Time before session expires automatically'
    },
    'auto_logout': {
      es: 'Cerrar Sesión Automáticamente',
      en: 'Auto Logout'
    },
    'auto_logout_desc': {
      es: 'Cierra la sesión cuando se cierre el navegador',
      en: 'Close session when browser is closed'
    },
    'data': {
      es: '💾 Datos',
      en: '💾 Data'
    },
    'auto_backup': {
      es: 'Respaldo Automático',
      en: 'Auto Backup'
    },
    'auto_backup_desc': {
      es: 'Realiza copias de seguridad automáticas de tus datos',
      en: 'Perform automatic backups of your data'
    },
    'backup_frequency': {
      es: 'Frecuencia de Respaldo',
      en: 'Backup Frequency'
    },
    'backup_frequency_desc': {
      es: 'Con qué frecuencia se realizan los respaldos',
      en: 'How often backups are performed'
    },
    'daily': {
      es: 'Diario',
      en: 'Daily'
    },
    'weekly': {
      es: 'Semanal',
      en: 'Weekly'
    },
    'monthly': {
      es: 'Mensual',
      en: 'Monthly'
    },
    'retention_days': {
      es: 'Días de Retención',
      en: 'Retention Days'
    },
    'retention_days_desc': {
      es: 'Cuántos días mantener los respaldos',
      en: 'How many days to keep backups'
    },
    'save_configuration': {
      es: 'Guardar Configuración',
      en: 'Save Configuration'
    },
    'saving': {
      es: 'Guardando...',
      en: 'Saving...'
    },
    'apply_changes': {
      es: 'Aplicar Cambios',
      en: 'Apply Changes'
    },
    'export_data': {
      es: 'Exportar Datos',
      en: 'Export Data'
    },
    'reset': {
      es: 'Restablecer',
      en: 'Reset'
    },
    'back_to_dashboard': {
      es: 'Volver al Dashboard',
      en: 'Back to Dashboard'
    },
    'configuration': {
      es: '⚙️ Configuración',
      en: '⚙️ Configuration'
    },
    'settings_saved': {
      es: 'Configuración guardada correctamente',
      en: 'Configuration saved successfully'
    },
    'settings_reset': {
      es: 'Configuración restablecida',
      en: 'Configuration reset'
    },
    'data_exported': {
      es: 'Datos exportados correctamente',
      en: 'Data exported successfully'
    },
    'error_saving': {
      es: 'Error al guardar la configuración',
      en: 'Error saving configuration'
    },
    'error_exporting': {
      es: 'Error al exportar datos',
      en: 'Error exporting data'
    },
    'language_changed': {
      es: 'Idioma cambiado a Español',
      en: 'Language changed to English'
    }
  };

  constructor() {
    this.initializeLanguage();
  }

  private initializeLanguage() {
    try {
      // Cargar idioma guardado
      const savedLanguage = localStorage.getItem('appLanguage');
      
      if (savedLanguage && (savedLanguage === 'es' || savedLanguage === 'en')) {
        this.currentLanguage = savedLanguage;
        console.log('🌐 Idioma cargado desde localStorage:', savedLanguage);
      } else {
        // Si no hay idioma guardado o es inválido, usar el idioma del navegador
        const browserLang = navigator.language.toLowerCase().startsWith('es') ? 'es' : 'en';
        this.currentLanguage = browserLang;
        localStorage.setItem('appLanguage', browserLang);
        console.log('🌐 Usando idioma del navegador:', browserLang);
      }

      // Aplicar el idioma al elemento HTML
      document.documentElement.lang = this.currentLanguage;
      document.documentElement.classList.remove('lang-es', 'lang-en');
      document.documentElement.classList.add(`lang-${this.currentLanguage}`);
      
      console.log('✅ Idioma inicializado correctamente:', this.currentLanguage);
    } catch (error) {
      console.error('❌ Error al inicializar el idioma:', error);
      // En caso de error, usar español como fallback
      this.currentLanguage = 'es';
      document.documentElement.lang = 'es';
      document.documentElement.classList.add('lang-es');
    }
  }

  setLanguage(language: 'es' | 'en') {
    try {
      console.log('🔄 Cambiando idioma a:', language);
      
      this.currentLanguage = language;
      localStorage.setItem('appLanguage', language);
      
      // Actualizar el idioma en el HTML
      document.documentElement.lang = language;
      document.documentElement.classList.remove('lang-es', 'lang-en');
      document.documentElement.classList.add(`lang-${language}`);
      
      console.log('✅ Idioma cambiado correctamente a:', language);
      return true;
    } catch (error) {
      console.error('❌ Error al cambiar el idioma:', error);
      return false;
    }
  }

  getCurrentLanguage(): string {
    return this.currentLanguage;
  }

  translate(key: string, params?: { [key: string]: string }): string {
    const translation = this.translations[key];
    if (!translation) {
      console.warn(`Translation key not found: ${key}`);
      return key;
    }

    let text = translation[this.currentLanguage as keyof typeof translation];
    
    // Reemplazar parámetros
    if (params) {
      Object.keys(params).forEach(param => {
        text = text.replace(`{{${param}}}`, params[param]);
      });
    }

    return text;
  }

  // Método para obtener todas las traducciones de una clave
  getAllTranslations(key: string): { es: string; en: string } | null {
    return this.translations[key] || null;
  }
} 