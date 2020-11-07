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
import {map, switchMap} from 'rxjs/operators';

import {Event} from 'src/app/events/events.service';
import {EventCreationDialogComponent} from 'src/app/events/event-creation-dialog.component';
import {GuildService} from './guild.service';

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

  readonly guild$ = this.route.paramMap.pipe(
    // Get guild ID we are currently browsing
    map(params => params.get('guildId') ?? ''),
    // Get the corresponding guild information
    switchMap(guildId => this.guildService.getGuild(guildId))
  );

  openCreateEventDialog() {
    const dialogRef = this.dialog.open(EventCreationDialogComponent, {data: {}});

    dialogRef.afterClosed().subscribe(result => {
      console.log(`Dialog results: ${result}`);
    });
  }

  /** Helps Angular keeping track of which event it already rendered. */
  trackByEventId(index: number, event: Event): string {
    return event.id;
  }
}
