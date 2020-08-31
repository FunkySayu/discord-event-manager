/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {AppCommonModule} from '../common.module';
import {AvatarComponent} from './avatar.component';

describe('IconComponent', () => {
  let component: AvatarComponent;
  let fixture: ComponentFixture<AvatarComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [AppCommonModule],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AvatarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('does not display an image if no href is provided', () => {
    const img = fixture.nativeElement.querySelector('img');
    expect(img).toBeNull();
  });

  it('displays an image relative to the Discord CDN', () => {
    component.type = 'avatars';
    component.id = '123';
    component.icon = '456';
    fixture.detectChanges();

    const img = fixture.nativeElement.querySelector('img');
    expect(img).not.toBeNull();
    expect(img.getAttribute('src')).toBe('https://cdn.discordapp.com/avatars/123/456.png');
  });
});
