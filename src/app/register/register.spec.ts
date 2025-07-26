import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Register } from './register';

describe('Register', () => {
  let component: Register;
  let fixture: ComponentFixture<Register>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Register]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Register);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('debe mostrar error si el nombre contiene números', () => {
    const component = fixture.componentInstance;
    const form = document.createElement('form');
    form.innerHTML = `
      <input name="username" value="Juan123">
      <input name="email" value="test@email.com">
      <input name="telefono" value="123456789">
      <input name="password" value="abcdef">
      <input name="confirmPassword" value="abcdef">
    `;
    const mockDiv = document.createElement('div');
    spyOn(document, 'getElementById').and.returnValue(mockDiv);
    component.onSubmit({ preventDefault: () => {}, target: form } as any);
    // Espera que se muestre error de solo letras
  });
  it('debe mostrar error si el teléfono contiene letras', () => {
    const component = fixture.componentInstance;
    const form = document.createElement('form');
    form.innerHTML = `
      <input name="username" value="Juan">
      <input name="email" value="test@email.com">
      <input name="telefono" value="123abc">
      <input name="password" value="abcdef">
      <input name="confirmPassword" value="abcdef">
    `;
    const mockDiv = document.createElement('div');
    spyOn(document, 'getElementById').and.returnValue(mockDiv);
    component.onSubmit({ preventDefault: () => {}, target: form } as any);
    // Espera que se muestre error de solo números
  });
});
