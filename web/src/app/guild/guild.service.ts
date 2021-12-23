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

import {Event} from 'src/app/events/events.service';
import {Timestamp} from 'src/app/common/time';
import {HTTP_OPTIONS} from 'src/app/common/http';

export declare interface Guild {
  id?: string;
  date_created?: Timestamp;
  date_modified?: Timestamp;
  discord_name?: string;
  icon_url?: string;
  bot_present?: boolean;
}

/** Accesses the general profile of the user. */
@Injectable({providedIn: 'root'})
export class GuildService {
  constructor(private readonly http: HttpClient) {}

  /** Returns the high level user profile. */
  getGuild(guildId: string): Observable<Guild> {
    return this.http.get<Guild>(`/api/guilds/${guildId}`);
  }

  /** Creates an event for a given guild. */
  createEvent(guildId: string, event: Event): Observable<Event> {
    return this.http.put<Event>(`/api/guilds/${guildId}/events`, event, HTTP_OPTIONS);
  }

  /** Associates a user to a guild. */
  registerPlayer(guildId: string, userId: string) {
    return this.http.put(`/api/guilds/${guildId}/players/${userId}`, {}, HTTP_OPTIONS);
  }
}
