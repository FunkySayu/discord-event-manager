import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-styles-demo',
  templateUrl: './styles-demo.component.html',
  styleUrls: ['./styles-demo.component.scss']
})
export class StylesDemoComponent implements OnInit {

  readonly palettes = ['red', 'orange', 'yellow', 'green', 'blue'];
  readonly weights = ['lightest', 'lighter', 'light', 'normal', 'dark', 'darker', 'darkest'];

  constructor() { }

  ngOnInit(): void {
  }

}
