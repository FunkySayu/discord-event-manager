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

import {Component, Inject} from '@angular/core';
import {MatDialogRef, MAT_DIALOG_DATA} from '@angular/material/dialog';
import {FormControl, FormGroup} from '@angular/forms';

import {assertNonNull} from 'src/app/common/asserts';
import {Timezone, ALL_TIMEZONES, TIMEZONE_NAMES, naiveConvertDateToTimestamp} from 'src/app/common/time';

import {Event} from './events.service';

/** Input provided to the modal, pre-configuring its inputs. */
export interface EventCreationDialogData {
  /** The default timezone to use. */
  timezone?: Timezone;
}

/** Created event by the dialog. */
export interface CreatedEvent {
  event: Event;
}

/** Routed component presenting the profile of a guild. */
@Component({
  templateUrl: './event-creation-dialog.component.html',
  styleUrls: ['./event-creation-dialog.component.scss'],
})
export class EventCreationDialogComponent {
  readonly ALL_TIMEZONES = ALL_TIMEZONES;
  readonly TIMEZONE_NAMES = TIMEZONE_NAMES;
  readonly TODAY = new Date();

  readonly formGroup = new FormGroup({
    title: new FormControl(''),
    description: new FormControl(''),
    date: new FormControl(''),
  })

  /** Currently selected timezone. */
  timezone: Timezone;

  constructor(
    @Inject(MAT_DIALOG_DATA) readonly data: EventCreationDialogData,
    private readonly dialogRef: MatDialogRef<EventCreationDialogComponent>
  ) {
    assertNonNull(this.data, 'EventCreationDialogComponent requires data to be passed.');

    this.timezone = this.data.timezone ?? ALL_TIMEZONES[0];
  }

  /** Attempts to create the event. Blocks the modal from closing, and log any potential errors. */
  createEvent() {
    const date: Date = this.formGroup.controls.date.value;
    date.setHours(13);
    date.setMinutes(37);

    const event: Event = {
      title: this.formGroup.controls.title.value,
      description: this.formGroup.controls.description.value,
      date: naiveConvertDateToTimestamp(date),
    };

    this.dialogRef.close(event);
  }
}
