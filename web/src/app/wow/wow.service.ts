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
import { map } from 'rxjs/operators';
import { Observable, of } from 'rxjs';

/** All the possible classes for a World of Warcraft character. */
export enum WowCharacterClass {
  DEATH_KNIGHT = 'DEATH_KNIGHT',
  DEMON_HUNTER = 'DEMON_HUNTER',
  DRUID = 'DRUID',
  HUNTER = 'HUNTER',
  MAGE = 'MAGE',
  MONK = 'MONK',
  PALADIN = 'PALADIN',
  PRIEST = 'PRIEST',
  ROGUE = 'ROGUE',
  SHAMAN = 'SHAMAN',
  WARLOCK = 'WARLOCK',
  WARRIOR = 'WARRIOR',
}

/** The 3 possible roles on World of Warcraft. */
export enum WowRole {
  TANK = 'TANK',
  DPS = 'DPS',
  HEALER = 'HEALER',
}

/** A world of warcraft character. */
export declare interface WowCharacter {
  name?: string;
  realm?: string;
  class?: WowCharacterClass;
  role?: WowRole;
  speciality?: string;
  ilvl?: number;
  icon_url?: string;
}

/** A sample character for testing. */
export const SAMPLE_CHARACTER: WowCharacter = {
  name: 'Funkypewpew',
  realm: 'Argent Dawn',
  class: WowCharacterClass.HUNTER,
  role: WowRole.DPS,
  speciality: 'Marksmanship',
  ilvl: 430,
  icon_url: 'http://render-eu.worldofwarcraft.com/character/argent-dawn/100/146666340-avatar.jpg',
};

/** Provides access to the WoW related routes. */
@Injectable({
  providedIn: 'root',
})
export class WowService {
  constructor(private readonly http: HttpClient) {}

  /** Checks if the user is authenticated on BattleNet. */
  isAuthenticated(): Observable<boolean> {
    return this.http.get<{authenticated: boolean}>('/auth/bnet/is_authenticated').pipe(
      map(response => !!response.authenticated),
    )
  }

  /** Returns the characters pulled from the Battle.net OAuth API. */
  getLoggedUserCharacters() {
    return this.http.get<{data: WowCharacter[]}>('/api/wow/me/characters').pipe(
      map(response => response.data ?? []),
    );
  }
}
