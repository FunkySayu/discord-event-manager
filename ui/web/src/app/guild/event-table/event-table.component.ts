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
import {DataSource} from '@angular/cdk/collections';
import {BehaviorSubject, Observable} from 'rxjs';
import {filter, map} from 'rxjs/operators';
import {state, style, trigger} from '@angular/animations';

import {Event} from 'src/app/events/events.service';
import {EventCreationDialogComponent} from 'src/app/events/event-creation-dialog.component';
import {SAMPLE_CHARACTER} from 'src/app/wow/wow.service';

/** Represents an expanded row. */
interface ExpandedEvent {
  detailRow: true;
  event: Event;
}

function isExpandedEvent(event: Event | ExpandedEvent): event is ExpandedEvent {
  return Object.prototype.hasOwnProperty.call(event, 'detailRow');
}

/**
 * Provides a data-source on all events available.
 *
 * The best way to handle expanded rows in Angular Material tables is to double
 * each rows and mark the double as an expanded one. This improves significantly
 * the internal tracking for Angular.
 */
class GuildEventTableDataSource extends DataSource<Event | ExpandedEvent> {
  /** Holds the original list of events received from the component. */
  private readonly originalEvents$ = new BehaviorSubject<readonly Event[]>([]);

  /** An observable on the doubled rows. */
  private readonly withExpanded$ = this.originalEvents$.pipe(
    map(events => events.reduce((acc, event) => acc.concat([event, {detailRow: true, event}]), []))
  );

  /** Returns the observable to the events and their expanded row. */
  connect(): Observable<Array<Event | ExpandedEvent>> {
    return this.withExpanded$;
  }

  /** Updates the original event list. */
  updateEventList(events: readonly Event[]) {
    this.originalEvents$.next(events);
  }

  /** Unimplemented but required by DataSource. */
  disconnect() {}
}

@Component({
  selector: 'guild-event-table',
  templateUrl: './event-table.component.html',
  styleUrls: ['./event-table.component.scss'],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({height: '0px', minHeight: '0', visibility: 'hidden', display: 'none'})),
      state('expanded', style({height: '*', visibility: 'visible'})),
    ]),
  ],
})
export class GuildEventTableComponent {
  /** Readonly value binding to access them from within the template. */
  readonly SAMPLE_CHARACTER = SAMPLE_CHARACTER;

  /** Tracks which element is currently expanded. */
  expandedEvent: unknown;
  /** Source on all events, including the expanded rows. */
  readonly dataSource = new GuildEventTableDataSource();
  /** List of columns normally displayed. */
  readonly displayedColumns: readonly string[] = ['title', 'date', 'wow-character', 'actions'];
  /** Checks whether a row is an expanded one or not. */
  readonly isExpandedRow = (index: number, event: Event | ExpandedEvent) => isExpandedEvent(event);

  constructor(private readonly dialog: MatDialog) {}

  @Input('events')
  set events(events: Event[]) {
    this.dataSource.updateEventList(events);
  }

  /** Emits whenever an event have been created by the user. */
  @Output() eventCreated = new EventEmitter<Event>();

  /** Explains to angular how to track events within a ngFor. */
  trackByEventId(index: number, event: Event | ExpandedEvent): string {
    return isExpandedEvent(event) ? `expanded::${event.event.id}` : `normal::${event.id}`;
  }

  openCreateEventDialog() {
    const dialogRef = this.dialog.open(EventCreationDialogComponent, {data: {}});

    const creationPipeline = dialogRef.afterClosed().pipe(
      // Only emit if the user actually created an event.
      filter(event => !!event)
    );
    creationPipeline.subscribe(event => {
      // Emit the event to the Output.
      this.eventCreated.next(event);
    });
  }
}
