import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ProviderService } from '../services/provider.service';

interface ProviderForm {
  id: string | null;
  nombre: string;
  telefono: string;
}

@Component({
  selector: 'app-providers',
  imports: [CommonModule, FormsModule],
  templateUrl: './providers.html',
  styleUrl: './providers.css'
})
export class Providers {
  proveedores: any[] = [];
  showAddModal = false;
  showEditModal = false;
  editForm: ProviderForm = { id: null, nombre: '', telefono: '' };

  constructor(
    private router: Router,
    private providerService: ProviderService
  ) {
    this.getAll();
  }

  getAll() {
    this.providerService.getProviders().subscribe({
      next: (data) => this.proveedores = data,
      error: (error) => {
        console.error('Error al obtener proveedores:', error);
        if (error.status === 401) {
          this.router.navigate(['/login']);
        }
      }
    });
  }

  addProvider(event: Event) {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const nombre = (form.elements.namedItem('nombre') as HTMLInputElement).value.trim();
    const telefono = (form.elements.namedItem('telefono') as HTMLInputElement).value.trim();
    
    if (!nombre) {
      alert('El nombre es obligatorio');
      return;
    }

    const soloNumeros = /^[0-9]+$/;
    if (!soloNumeros.test(telefono)) {
      alert('El teléfono solo puede contener números');
      return;
    }

    this.providerService.createProvider({ nombre, telefono }).subscribe({
      next: () => {
        this.getAll();
        this.showAddModal = false;
      },
      error: (error) => {
        console.error('Error al crear proveedor:', error);
        if (error.status === 401) {
          alert('Debes iniciar sesión para registrar un proveedor.');
          this.router.navigate(['/login']);
        } else {
          alert('Error al crear el proveedor. Por favor, intenta de nuevo.');
        }
      }
    });
  }

  edit(p: any) {
    this.editForm = { id: p.id, nombre: p.nombre, telefono: p.telefono };
    this.showEditModal = true;
  }

  editProvider(event: Event) {
    event.preventDefault();
    const { id, nombre, telefono } = this.editForm;
    
    if (id && nombre && telefono) {
      this.providerService.updateProvider(id, { nombre, telefono }).subscribe({
        next: () => {
          this.getAll();
          this.showEditModal = false;
        },
        error: (error) => {
          console.error('Error al actualizar proveedor:', error);
          if (error.status === 401) {
            alert('Debes iniciar sesión para editar un proveedor.');
            this.router.navigate(['/login']);
          } else {
            alert('Error al actualizar el proveedor. Por favor, intenta de nuevo.');
          }
        }
      });
    }
  }

  delete(p: any) {
    if (confirm('¿Eliminar proveedor?')) {
      this.providerService.deleteProvider(p.id).subscribe({
        next: () => this.getAll(),
        error: (error) => {
          console.error('Error al eliminar proveedor:', error);
          if (error.status === 401) {
            alert('Debes iniciar sesión para eliminar un proveedor.');
            this.router.navigate(['/login']);
          } else {
            alert('Error al eliminar el proveedor. Por favor, intenta de nuevo.');
          }
        }
      });
    }
  }

  openEditModal(p: any) {
    this.editForm = { id: p.id, nombre: p.nombre, telefono: p.telefono };
    this.showEditModal = true;
  }

  confirmDelete(p: any) {
    if (confirm('¿Eliminar proveedor?')) {
      this.delete(p);
    }
  }

  openAddModal() {
    this.showAddModal = true;
    this.editForm = { id: null, nombre: '', telefono: '' };
  }

  goToDashboard() {
    this.router.navigate(['/dashboard']);
  }
}
