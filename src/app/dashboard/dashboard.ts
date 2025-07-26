import { Component, OnInit } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { TranslationService } from '../services/translation.service';
import { SharedModule } from '../shared';
import { DashboardService, Activity } from '../services/dashboard.service';

interface Notification {
  id: number;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: Date;
}

@Component({
  selector: 'app-dashboard',
  imports: [RouterModule, CommonModule, SharedModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  username = '';
  loginDate = '';
  showUserMenu = false;
  notifications: Notification[] = [];
  recentActivity: Activity[] = [];

  constructor(
    private router: Router,
    private dashboardService: DashboardService,
    public translationService: TranslationService
  ) {}

  ngOnInit() {
    this.loadUserInfo();
    this.loadRecentActivity();
    this.showWelcomeNotification();
  }

  loadUserInfo() {
    this.username = localStorage.getItem('username') || 'Usuario';
    const storedDate = localStorage.getItem('loginDate');
    if (storedDate) {
      this.loginDate = storedDate;
    } else {
      const now = new Date();
      this.loginDate = now.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      localStorage.setItem('loginDate', this.loginDate);
    }
  }

  loadRecentActivity() {
    this.dashboardService.getRecentActivity().subscribe({
      next: (data: Activity[]) => {
        this.recentActivity = data;
      },
      error: (error: unknown) => {
        console.error('Error cargando actividad reciente:', error);
        // Fallback a datos por defecto si hay error
        this.recentActivity = [
          {
            id: 1,
            type: 'product',
            title: this.translationService.translate('new_product_added'),
            description: this.translationService.translate('product_added_description'),
            time: this.translationService.translate('ago_5_minutes')
          },
          {
            id: 2,
            type: 'category',
            title: this.translationService.translate('category_updated'),
            description: this.translationService.translate('category_updated_description'),
            time: this.translationService.translate('ago_15_minutes')
          },
          {
            id: 3,
            type: 'provider',
            title: this.translationService.translate('provider_registered'),
            description: this.translationService.translate('provider_registered_description'),
            time: this.translationService.translate('ago_1_hour')
          },
        ];
      }
    });
  }

  showWelcomeNotification() {
    this.addNotification({
      type: 'success',
      title: this.translationService.translate('welcome_message'),
      message: this.translationService.translate('welcome_description')
    });
  }

  addNotification(notification: Omit<Notification, 'id' | 'timestamp'>) {
    const newNotification: Notification = {
      ...notification,
      id: Date.now(),
      timestamp: new Date()
    };
    this.notifications.push(newNotification);

    // Auto-remover notificación después de 5 segundos
    setTimeout(() => {
      this.removeNotification(this.notifications.length - 1);
    }, 5000);
  }

  removeNotification(index: number) {
    this.notifications.splice(index, 1);
  }

  toggleUserMenu() {
    this.showUserMenu = !this.showUserMenu;
  }

  navigateTo(route: string) {
    this.router.navigate([route]);
  }

  logout() {
    // Agregar notificación de cierre de sesión
    this.addNotification({
      type: 'info',
      title: this.translationService.translate('closing_session'),
      message: this.translationService.translate('logout_message')
    });

    // Limpiar datos de sesión después de un breve delay
    setTimeout(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('loginDate');
      window.location.href = '/';
    }, 1000);
  }

  // Método para acceder a Math desde el template
  get Math() {
    return Math;
  }
}
