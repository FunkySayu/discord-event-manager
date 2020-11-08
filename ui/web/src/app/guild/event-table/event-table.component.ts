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

import {Component, Input, Output, EventEmitter} from '@angular/core';
import {MatDialog} from '@angular/material/dialog';
import {filter} from 'rxjs/operators';

import {Event} from 'src/app/events/events.service';
import {EventCreationDialogComponent} from 'src/app/events/event-creation-dialog.component';


@Component({
  selector: 'guild-event-table',
  templateUrl: './event-table.component.html',
  styleUrls: ['./event-table.component.scss'],
})
export class GuildEventTableComponent {
  /** The list of events to display. */
  @Input() events: Event[] = [];
  /** Emits whenever an event have been created by the user. */
  @Output() eventCreated = new EventEmitter<Event>();

  constructor(private readonly dialog: MatDialog) {}

  /** Explains to angular how to track events within a ngFor. */
  trackByEventId(index: number, event: Event): string {
    return event.id;
  }

  openCreateEventDialog() {
    const dialogRef = this.dialog.open(EventCreationDialogComponent, {data: {}});

    const creationPipeline = dialogRef.afterClosed().pipe(
      // Only emit if the user actually created an event.
      filter(event => !!event));
    creationPipeline.subscribe(event => {
      this.eventCreated.next(event);
    });
  }
}
