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

import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {map, mapTo} from 'rxjs/operators';

import {Guild} from '../guild/guild.service';
import { CachedEndpoint } from '../common/http';

/** Permission level of an user over a guild. */
export declare enum Permission {
  NONE = 'NONE',
  VISIBLE = 'VISIBLE',
  OWNER = 'OWNER',
}

export declare interface GuildRelationship {
  guild?: Guild;
  permission?: Permission;
}

/** A Discord user. */
export declare interface UserProfile {
  id?: number;
  username?: string;
  discriminator?: string;
  icon_url?: string;
  guilds?: GuildRelationship[];
}

/** Response to the authentication check. */
interface AuthCheckResponse {
  authenticated?: boolean;
}

/** Accesses the general profile of the user. */
@Injectable({
  providedIn: 'root',
})
export class UserService {
  private readonly userProfile$ = new CachedEndpoint(
    () => this.http.get<UserProfile>('/api/user'));
  
  constructor(private readonly http: HttpClient) {}

  /** Returns the high level user profile. */
  getUserProfile(): Observable<UserProfile> {
    return this.userProfile$.get();
  }

  /** Checks if the user is currently authenticated. */
  isAuthenticated(): Observable<boolean> {
    return this.http
      .get<AuthCheckResponse>('/auth/discord/is_authenticated')
      .pipe(map(response => !!response?.authenticated));
  }

  /** Logs out the user. */
  logout(): Observable<void> {
    return this.http.get('/auth/discord/logout').pipe(mapTo(undefined));
  }
}
