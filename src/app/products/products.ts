import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ProductService } from '../services/product.service';
import { CategoryService } from '../services/category.service';

interface ProductForm {
  id: string | null;
  nombre: string;
  categoria: string;
  descripcion: string;
  precio: string;
}

@Component({
  selector: 'app-products',
  imports: [CommonModule, FormsModule],
  templateUrl: './products.html',
  styleUrl: './products.css'
})
export class Products {
  productos: any[] = [];
  categorias: any[] = [];
  showAddModal = false;
  showEditModal = false;
  editForm: ProductForm = { id: null, nombre: '', categoria: '', descripcion: '', precio: '' };

  constructor(
    private router: Router,
    private productService: ProductService,
    private categoryService: CategoryService
  ) {
    this.getAll();
    this.getCategorias();
  }

  getAll() {
    this.productService.getProducts().subscribe({
      next: (data) => this.productos = data,
      error: (error) => {
        console.error('Error al obtener productos:', error);
        if (error.status === 401) {
          this.router.navigate(['/login']);
        }
      }
    });
  }

  getCategorias() {
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

  addProduct(event: Event) {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const nombre = (form.elements.namedItem('nombre') as HTMLInputElement).value.trim();
    const categoria = (form.elements.namedItem('categoria') as HTMLInputElement).value.trim();
    const descripcion = (form.elements.namedItem('descripcion') as HTMLInputElement).value.trim();
    const precioStr = (form.elements.namedItem('precio') as HTMLInputElement).value;
    const precio = parseFloat(precioStr);

    const soloLetras = /^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$/;
    if (!soloLetras.test(nombre)) {
      alert('El nombre solo puede contener letras');
      return;
    }
    if (!categoria) {
      alert('Selecciona una categoría');
      return;
    }
    if (!descripcion) {
      alert('La descripción es obligatoria');
      return;
    }
    if (!/^[0-9]+(\.[0-9]{1,2})?$/.test(precioStr)) {
      alert('El precio solo puede contener números');
      return;
    }

    if (nombre && categoria && descripcion && !isNaN(precio)) {
      this.productService.createProduct({ nombre, categoria, descripcion, precio }).subscribe({
        next: () => {
          this.getAll();
          this.showAddModal = false;
        },
        error: (error) => {
          console.error('Error al crear producto:', error);
          if (error.status === 401) {
            alert('Debes iniciar sesión para registrar un producto.');
            this.router.navigate(['/login']);
          } else {
            alert('Error al crear el producto. Por favor, intenta de nuevo.');
          }
        }
      });
    }
  }

  edit(p: any) {
    this.editForm = { id: p.id, nombre: p.nombre, categoria: p.categoria, descripcion: p.descripcion, precio: p.precio };
    this.showEditModal = true;
  }

  editProduct(event: Event) {
    event.preventDefault();
    const { id, nombre, categoria, descripcion, precio } = this.editForm;
    
    if (id && nombre && categoria && descripcion && precio) {
      this.productService.updateProduct(id, { 
        nombre, 
        categoria, 
        descripcion, 
        precio: parseFloat(precio) 
      }).subscribe({
        next: () => {
          this.getAll();
          this.showEditModal = false;
        },
        error: (error) => {
          console.error('Error al actualizar producto:', error);
          if (error.status === 401) {
            alert('Debes iniciar sesión para editar un producto.');
            this.router.navigate(['/login']);
          } else {
            alert('Error al actualizar el producto. Por favor, intenta de nuevo.');
          }
        }
      });
    }
  }

  delete(p: any) {
    if (confirm('¿Eliminar producto?')) {
      this.productService.deleteProduct(p.id).subscribe({
        next: () => this.getAll(),
        error: (error) => {
          console.error('Error al eliminar producto:', error);
          if (error.status === 401) {
            alert('Debes iniciar sesión para eliminar un producto.');
            this.router.navigate(['/login']);
          } else {
            alert('Error al eliminar el producto. Por favor, intenta de nuevo.');
          }
        }
      });
    }
  }

  getCategoryColor(cat: string) { return '#6366f1'; }
  
  openEditModal(p: any) {
    this.editForm = { id: p.id, nombre: p.nombre, categoria: p.categoria, descripcion: p.descripcion, precio: p.precio };
    this.showEditModal = true;
  }
  
  confirmDelete(p: any) {
    if (confirm('¿Eliminar producto?')) {
      this.delete(p);
    }
  }
  
  viewDetails(p: any) {}
  
  openAddModal() {
    this.showAddModal = true;
    this.editForm = { id: null, nombre: '', categoria: '', descripcion: '', precio: '' };
  }
  
  goToDashboard() {
    this.router.navigate(['/dashboard']);
  }
}
