import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CategoryService } from '../services/category.service';

interface CategoryForm {
  id: string | null;
  nombre: string;
  descripcion: string;
}

@Component({
  selector: 'app-categories',
  imports: [CommonModule, FormsModule],
  templateUrl: './categories.html',
  styleUrl: './categories.css'
})
export class Categories {
  categorias: any[] = [];
  showAddModal = false;
  showEditModal = false;
  editForm: CategoryForm = { id: null, nombre: '', descripcion: '' };

  constructor(
    private router: Router,
    private categoryService: CategoryService
  ) {
    this.getAll();
  }

  getAll() {
    this.categoryService.getCategories().subscribe({
      next: (data) => this.categorias = data,
      error: (error) => {
        console.error('Error al obtener categorías:', error);
        if (error.status === 401) {
          this.router.navigate(['/login']);
        }
      }
    });
  }

  addCategory(event: Event) {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const nombre = (form.elements.namedItem('nombre') as HTMLInputElement).value.trim();
    const descripcion = (form.elements.namedItem('descripcion') as HTMLInputElement).value.trim();

    if (!nombre) {
      alert('El nombre es obligatorio');
      return;
    }

    if (!descripcion) {
      alert('La descripción es obligatoria');
      return;
    }

    this.categoryService.createCategory({ nombre, descripcion }).subscribe({
      next: () => {
        this.getAll();
        this.showAddModal = false;
      },
      error: (error) => {
        console.error('Error al crear categoría:', error);
        if (error.status === 401) {
          alert('Debes iniciar sesión para registrar una categoría.');
          this.router.navigate(['/login']);
        } else {
          alert('Error al crear la categoría. Por favor, intenta de nuevo.');
        }
      }
    });
  }

  edit(c: any) {
    this.editForm = { id: c.id, nombre: c.nombre, descripcion: c.descripcion };
    this.showEditModal = true;
  }

  editCategory(event: Event) {
    event.preventDefault();
    const { id, nombre, descripcion } = this.editForm;
    
    if (id && nombre && descripcion) {
      this.categoryService.updateCategory(id, { nombre, descripcion }).subscribe({
        next: () => {
          this.getAll();
          this.showEditModal = false;
        },
        error: (error) => {
          console.error('Error al actualizar categoría:', error);
          if (error.status === 401) {
            alert('Debes iniciar sesión para editar una categoría.');
            this.router.navigate(['/login']);
          } else {
            alert('Error al actualizar la categoría. Por favor, intenta de nuevo.');
          }
        }
      });
    }
  }

  delete(c: any) {
    if (confirm('¿Eliminar categoría?')) {
      this.categoryService.deleteCategory(c.id).subscribe({
        next: () => this.getAll(),
        error: (error) => {
          console.error('Error al eliminar categoría:', error);
          if (error.status === 401) {
            alert('Debes iniciar sesión para eliminar una categoría.');
            this.router.navigate(['/login']);
          } else {
            alert('Error al eliminar la categoría. Por favor, intenta de nuevo.');
          }
        }
      });
    }
  }

  openAddModal() {
    this.showAddModal = true;
    this.editForm = { id: null, nombre: '', descripcion: '' };
  }

  openEditModal(c: any) {
    this.editForm = { id: c.id, nombre: c.nombre, descripcion: c.descripcion };
    this.showEditModal = true;
  }

  confirmDelete(c: any) {
    if (confirm('¿Eliminar categoría?')) {
      this.delete(c);
    }
  }

  goToDashboard() {
    this.router.navigate(['/dashboard']);
  }
}
