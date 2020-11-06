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

import {Timestamp} from 'src/app/common/typing';

/**
 * The repetition frequency of an event.
 *
 * Needs to be kept in sync with: ui/mod_event/event.py:EventRepetitionFrequency.
 */
export declare enum EventRepetitionFrequency {
  NOT_REPEATED = 'NOT_REPEATED',
  DAILY = 'DAILY',
  WEEKLY = 'WEEKLY',
}

/**
 * An event, as per the definition in the backend.
 *
 * Field names need to be kept in sync with: ui/mod_event/event.py:Event.
 */
export declare interface Event {
  id?: string;
  date_created?: Timestamp;
  date_modified?: Timestamp;
  parent_id?: string;
  title?: string;
  description?: string;
  timezone_name?: string;
  repetition?: EventRepetitionFrequency;
}

/** Provides access to the events. */
@Injectable({providedIn: 'root'})
export class EventsService {
  constructor(private readonly http: HttpClient) {}

  /** Returns the high level user profile. */
  getEvent(id: string): Observable<Event> {
    return this.http.get<Event>(`/api/events/${id}`);
  }

  /**
   * Returns the next occurrence of the given event.
   *
   * This assumes the event is a repeated one; if it is not, the server will fail with
   * a 412 error.
   */
   getNextEvent(id: string): Observable<Event> {
     return this.http.get<Event>(`/api/events/${id}:next`);
   }
}
