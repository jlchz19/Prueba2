import { Routes, CanActivateFn } from '@angular/router';
import { Login } from './login/login';
import { Register } from './register/register';
import { VerifyEmail } from './verify-email/verify-email';
import { Dashboard } from './dashboard/dashboard';
import { Products } from './products/products';
import { Categories } from './categories/categories';
import { Providers } from './providers/providers';
import { Profile } from './profile/profile';
import { Settings } from './settings/settings';
import { ForgotPassword } from './login/forgot-password';

export const authGuard: CanActivateFn = () => {
  return !!localStorage.getItem('token');
};

export const routes: Routes = [
  { path: '', component: Login },
  { path: 'register', component: Register },
  { path: 'verify-email', component: VerifyEmail },
  { path: 'forgot-password', component: ForgotPassword },
  { path: 'products', component: Products, canActivate: [authGuard] },
  { path: 'categories', component: Categories, canActivate: [authGuard] },
  { path: 'providers', component: Providers, canActivate: [authGuard] },
  { path: 'profile', component: Profile, canActivate: [authGuard] },
  { path: 'settings', component: Settings, canActivate: [authGuard] },
  {
    path: 'dashboard',
    component: Dashboard,
    canActivate: [authGuard],
    // Ya no tiene children
  }
];
