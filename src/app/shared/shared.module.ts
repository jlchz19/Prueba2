import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslationService } from '../services/translation.service';

@NgModule({
  imports: [
    CommonModule
  ],
  providers: [
    TranslationService
  ],
  exports: [
    CommonModule
  ]
})
export class SharedModule { } 