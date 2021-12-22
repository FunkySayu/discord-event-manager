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

import {HttpHeaders, HttpClient} from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { shareReplay, switchMap } from 'rxjs/operators';

/** Http options shared across the application. */
export const HTTP_OPTIONS = {
  headers: new HttpHeaders({
    'Content-Type': 'application/json',
    Accept: 'application/json',
  }),
};

/**
 * Provides a cached endpoint interface, avoiding re-issuing requests
 * if a result was already available.
 */
export class CachedEndpoint<T> {
  /** Every emission on this subject will force a reset on the cache. */
  private readonly resetor$ = new BehaviorSubject<void>(undefined);
  /** Observable on the request. */
  private readonly data$ = this.resetor$.pipe(
    // Request the data when the resetor is triggered.
    switchMap(() => this.requestor()),
    // Share the last result.
    shareReplay(1));

  constructor(private readonly requestor: () => Observable<T>) {}

  /** Returns an observable on the data. */
  get(): Observable<T> {
    return this.data$;
  }
}