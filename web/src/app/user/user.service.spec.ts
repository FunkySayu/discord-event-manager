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

import {TestBed, getTestBed} from '@angular/core/testing';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';

import {UserModule} from './user.module';
import {UserService} from './user.service';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, UserModule],
    });
    const injector = getTestBed();
    service = injector.get(UserService);
    httpMock = injector.get(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('isAuthenticated', () => {
    it('checks the response content', () => {
      let response: boolean | undefined;
      service.isAuthenticated().subscribe(isAuthenticated => {
        response = isAuthenticated;
      });

      const req = httpMock.expectOne('/auth/discord/is_authenticated');
      expect(req.request.method).toBe('GET');
      req.flush({authenticated: true});

      expect(response).toBeDefined('no response retrieved');
      expect(response).toBeTruthy();
    });
  });
});
