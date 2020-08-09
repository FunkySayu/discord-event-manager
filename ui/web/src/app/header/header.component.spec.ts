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

import {async, fakeAsync, tick, ComponentFixture, TestBed} from '@angular/core/testing';
import {RouterTestingModule} from '@angular/router/testing';
import {HttpClientTestingModule} from '@angular/common/http/testing';

import {UserProfile} from '../user/user.service';

import {HeaderModule} from './header.module';
import {HeaderComponent} from './header.component';

describe('HeaderComponent', () => {
  let component: HeaderComponent;
  let fixture: ComponentFixture<HeaderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, RouterTestingModule, HeaderModule],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('provides a link to login to discord if no user is retrieved', () => {
    const loginButton = fixture.nativeElement.querySelector('a.login');
    expect(loginButton).not.toBeNull();
    expect(loginButton.getAttribute('href')).toBe('/auth/discord/oauth');
  });

  it('displays the user avatar instead of the login button after auth', () => {
    const profile: UserProfile = {
      guilds: [],
      user: {id: '123', avatar: '456'},
    };
    component.profile = profile;
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('a.login')).toBeNull();
    const userButton = fixture.nativeElement.querySelector('button.user-profile');
    expect(userButton).not.toBeNull();
    expect(userButton.querySelector('discord-icon img')).not.toBeNull();
  });

  it('selects a guild by default if none are selected', fakeAsync(() => {
    const profile: UserProfile = {
      guilds: [{id: '123', name: 'My amazing guild', icon: '456'}],
    };
    component.profile = profile;
    component.ngOnChanges();
    fixture.detectChanges();
    // Guild default selection happens on the next cycle; wait for it.
    tick(1);

    const guildSelector = fixture.nativeElement.querySelector('button.guild-selection');
    expect(guildSelector).not.toBeNull();
    expect(guildSelector.querySelector('discord-icon img')).not.toBeNull();
    expect(guildSelector.textContent).toContain('My amazing guild');
  }));
});
