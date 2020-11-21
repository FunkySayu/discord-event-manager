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

import {Component} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {MatDialog} from '@angular/material/dialog';
import {BehaviorSubject} from 'rxjs';
import {map, switchMap} from 'rxjs/operators';

import {CharacterSelectionDialogComponent} from 'src/app/wow/character-selection-dialog/character-selection-dialog.component';
import {Event} from 'src/app/events/events.service';

import {GuildService, Guild} from './guild.service';

/** Routed component presenting the profile of a guild. */
@Component({
  selector: 'guild-profile',
  templateUrl: './guild-profile.component.html',
  styleUrls: ['./guild-profile.component.scss'],
})
export class GuildProfileComponent {
  constructor(
    private readonly guildService: GuildService,
    private readonly route: ActivatedRoute,
    private readonly dialog: MatDialog
  ) {}

  /** Allows to trigger reload of the guild information based on emission on this observable. */
  private readonly reloader$ = new BehaviorSubject<void>(undefined);

  /** Queries the guild from the ID contained in the route. */
  readonly guild$ = this.reloader$.pipe(
    // Get guild ID we are currently browsing
    map(() => this.route.snapshot.paramMap.get('guildId') ?? ''),
    // Get the corresponding guild information
    switchMap(guildId => this.guildService.getGuild(guildId))
  );

  /** Calls the backend to create the provided event for the guild. */
  async createGuildEvent(guild: Guild, event: Event) {
    // TODO(funkysayu): Subscribe to the pipeline without caring much about the result.
    // Ideally we should have a snackbar indicating loading of the request and an error
    // handler somewhere.
    await this.guildService.createEvent(guild.id, event).toPromise();
    this.reloader$.next();
  }

  /** Associates a character to the current user. */
  associateCharacter() {
    const dialogRef = this.dialog.open(CharacterSelectionDialogComponent, {data: {}});

    dialogRef.afterClosed().subscribe(data => {
      console.log('data', data);
    });
  }
}
