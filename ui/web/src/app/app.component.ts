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

import { Component } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { catchError, shareReplay } from 'rxjs/operators';

import { UserService } from './user/user.service';

/** Base component of the application. */
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'web';

  constructor(private readonly userService: UserService) { }

  profile$ = this.userService.getUserProfile().pipe(
    // In case of error, check if it's a 401 and emit null.
    catchError(error => {
      if (error instanceof HttpErrorResponse && error.status === 401) {
        return of(null);
      }
      return throwError(error);
    }),
    // Share the result of the profile.
    shareReplay(1));
}
