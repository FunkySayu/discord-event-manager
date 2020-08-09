import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StylesDemoComponent } from './styles-demo/styles-demo.component';



@NgModule({
  declarations: [StylesDemoComponent],
  exports: [StylesDemoComponent],
  imports: [
    CommonModule
  ],
})
export class DemoModule { }
