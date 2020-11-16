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
import {FormControl, FormGroup, Validators} from '@angular/forms';

import {assertNonNull} from 'src/app/common/asserts';
import {Timezone, ALL_TIMEZONES, TIMEZONE_NAMES, naiveConvertDateToTimestamp} from 'src/app/common/time';

import {Event, ALL_REPETITIONS, REPETITION_NAMES} from './events.service';

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
  /** Constant binding to access them from within the template. */
  readonly ALL_TIMEZONES = ALL_TIMEZONES;
  readonly TIMEZONE_NAMES = TIMEZONE_NAMES;
  readonly ALL_REPETITIONS = ALL_REPETITIONS;
  readonly REPETITION_NAMES = REPETITION_NAMES;
  readonly TODAY = new Date();

  readonly formGroup = new FormGroup({
    title: new FormControl('', [Validators.required, Validators.minLength(4), Validators.maxLength(32)]),
    description: new FormControl(''),
    date: new FormControl('', [Validators.required]),
    hours: new FormControl(19, [Validators.required, Validators.min(0), Validators.max(23)]),
    minutes: new FormControl(30, [Validators.required, Validators.min(0), Validators.max(59)]),
  });

  /** Currently selected timezone. */
  timezone: Timezone | 'SERVER_DEFAULT';
  /** Currently selected repetition. */
  repetition = ALL_REPETITIONS[0];

  constructor(
    @Inject(MAT_DIALOG_DATA) readonly data: EventCreationDialogData,
    private readonly dialogRef: MatDialogRef<EventCreationDialogComponent>
  ) {
    assertNonNull(this.data, 'EventCreationDialogComponent requires data to be passed.');

    this.timezone = this.data.timezone ?? 'SERVER_DEFAULT';
  }

  /** Attempts to create the event. Blocks the modal from closing, and log any potential errors. */
  createEvent() {
    const date: Date = this.formGroup.controls.date.value;
    date.setHours(this.formGroup.controls.hours.value);
    date.setMinutes(this.formGroup.controls.minutes.value);

    const event: Event = {
      title: this.formGroup.controls.title.value,
      description: this.formGroup.controls.description.value,
      date: naiveConvertDateToTimestamp(date),
      repetition: this.repetition,
    };
    if (this.timezone !== 'SERVER_DEFAULT') {
      event.timezone_name = this.timezone;
    }

    this.dialogRef.close(event);
  }
}
