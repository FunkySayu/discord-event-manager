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

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


/** High level information about an user. */
export interface UserProfile {
  // TODO(funkysayu): fill this interface.
}


/** Accesses the general profile of the user. */
@Injectable({
  providedIn: 'root'
})
export class UserService {
  constructor(private readonly http: HttpClient) { }

  /** Returns the high level user profile. */
  getUserProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>('/api/user');
  }
}
