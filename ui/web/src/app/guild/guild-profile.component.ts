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
import {filter, map, switchMap} from 'rxjs/operators';

import {Event} from 'src/app/events/events.service';
import {EventCreationDialogComponent} from 'src/app/events/event-creation-dialog.component';
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

  readonly guild$ = this.route.paramMap.pipe(
    // Get guild ID we are currently browsing
    map(params => params.get('guildId') ?? ''),
    // Get the corresponding guild information
    switchMap(guildId => this.guildService.getGuild(guildId))
  );

  openCreateEventDialog(guild: Guild) {
    const dialogRef = this.dialog.open(EventCreationDialogComponent, {data: {}});

    const creationPipeline = dialogRef.afterClosed().pipe(
      // Only initiate some requests an event was provided.
      filter(value => !!value),
      // Initiate the creation of the event in the backend.
      switchMap((event: Event) => this.guildService.createEvent(guild.id, event))
    );

    // TODO(funkysayu): Subscribe to the pipeline without caring much about the result.
    // Ideally we should have a snackbar indicating loading of the request and an error
    // handler somewhere.
    // We should also force a reload of the guild whenever we get a positive result from
    // the backend.
    creationPipeline.subscribe(result => {
      console.log(result);
    });
  }
}
