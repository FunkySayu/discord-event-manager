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
import {map} from 'rxjs/operators';


/** Represents a World of Warcraft region. */
export type Region = string;


/** The two available factions in WoW. */
export enum WowFaction {
  HORDE = 'HORDE',
  ALLIANCE = 'ALLIANCE',
}


/** A world of warcraft realm. */
export declare interface WowRealm {
  name?: string;
  slug?: string;
  region?: Region;
  timezone_name?: string;
}


/** A world of warcraft playable speciality of a class. */
export declare interface WowPlayableSpec {
  name?: string;
  role?: string;
  klass?: WowPlayableClass;
}


/** A world of warcraft playable class. */
export declare interface WowPlayableClass {
  name?: string;
  specs?: WowPlayableSpec[];
}


/** A world of warcraft character. */
export declare interface WowCharacter {
  name?: string;
  realm?: WowRealm;
  faction?: WowFaction;
  klass?: WowPlayableClass;
  active_spec?: WowPlayableSpec;
  average_ilvl?: number;
  equipped_ilvl?: number;
  icon_url?: string;
}


/** A sample character for testing. */
export const SAMPLE_CHARACTER: WowCharacter = {
  name: 'Funkypewpew',
  realm: {name: 'Argent Dawn', slug: 'argent-dawn'},
  klass: {name: 'Hunter', specs: []},
  //role: WowRole.DPS,
  //speciality: 'Marksmanship',
  average_ilvl: 430,
  icon_url: 'http://render-eu.worldofwarcraft.com/character/argent-dawn/100/146666340-avatar.jpg',
};


/** Provides access to the WoW related routes. */
@Injectable({
  providedIn: 'root',
})
export class WowService {
  constructor(private readonly http: HttpClient) {}

  /** Get all regions supported by the application. */
  getRegions(): Observable<Region[]> {
    return this.http.get<{regions: Region[]}>('/api/wow/region/').pipe(
      map(response => response?.regions ?? []));
  }

  /** Get the world of warcraft realms associated with a region. */
  getRealms(region: Region): Observable<WowRealm[]> {
    return this.http.get<{realms: WowRealm[]}>(`/api/wow/region/${region}/realm/`).pipe(
      map(response => response?.realms ?? []));
  }

  /** Gets a character from the world of warcraft api. */
  getCharacter(region: Region, realmSlug: string, character: string): Observable<WowCharacter> {
    return this.http.get(`/api/wow/region/${region}/realm/${realmSlug}/character/${character}`);
  }
}
