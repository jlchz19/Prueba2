import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css'
})
export class Sidebar implements OnInit {
  usuario: string | null = null;
  sidebarCollapsed = false;
  constructor(private router: Router) {
    this.usuario = localStorage.getItem('username');
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.usuario = localStorage.getItem('username');
      }
    });
  }
  ngOnInit() {
    this.usuario = localStorage.getItem('username');
  }
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    this.router.navigate(['/']);
  }
  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }
}
