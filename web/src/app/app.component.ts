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

import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {of} from 'rxjs';
import {shareReplay, switchMap} from 'rxjs/operators';

import {UserService} from './user/user.service';
import {Guild} from './guild/guild.service';

/** Base component of the application. */
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  selectedGuild?: Guild;

  constructor(private readonly userService: UserService, private readonly router: Router) {}

  /** Verifies who is the current authenticated user. */
  private readonly authenticated$ = this.userService.isAuthenticated().pipe(shareReplay(1));

  /** Retrieves the profile of the current active user. */
  readonly profile$ = this.authenticated$.pipe(
    // Emit null if the user is not authenticated, otherwise get its profile.
    switchMap(logged => (logged ? this.userService.getUserProfile() : of(null))),
    // Share the result of the profile.
    shareReplay(1)
  );

  /** Redirects the user on depending of the authentication check. */
  ngOnInit() {
    this.authenticated$.subscribe(isAuthenticated => {
      if (!isAuthenticated) {
        this.router.navigate(['/landing']);
      }
    });
  }

  /** Navigates to the guild profile. */
  navigateToGuild(guild?: Guild) {
    if (!guild?.id) {
      return;
    }
    this.router.navigate(['guild', guild.id]);
  }
}
