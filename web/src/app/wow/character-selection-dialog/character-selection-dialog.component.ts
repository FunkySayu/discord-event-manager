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
import {combineLatest} from 'rxjs';

import {WowService} from '../wow.service';

interface CharacterSelectionDialogComponentData {
  stuff?: undefined;
}

@Component({
  selector: 'character-selection-dialog',
  templateUrl: './character-selection-dialog.component.html',
  styleUrls: ['./character-selection-dialog.component.scss'],
})
export class CharacterSelectionDialogComponent {
  /** Form controllers and validators. */
  readonly formGroup = new FormGroup({
    region: new FormControl('', [Validators.required]),
    realm: new FormControl('', [Validators.required]),
    character: new FormControl('', [Validators.required, Validators.minLength(3), Validators.maxLength(12)]),
  });

  constructor(
    @Inject(MAT_DIALOG_DATA) readonly data: CharacterSelectionDialogComponentData,
    private readonly dialogRef: MatDialogRef<CharacterSelectionDialogComponent>,
    private readonly wowService: WowService
  ) {}

  /** Listeners on the current form selection. */
  private readonly selectedRegion$ = this.formGroup.get('region').valueChanges;
  private readonly selectedRealm$ = this.formGroup.get('realm').valueChanges;
  private readonly selectedCharacter$ = this.formGroup.get('character').valueChanges;

  /** Temporary debugging string. */
  readonly debug$ = combineLatest([this.selectedRegion$, this.selectedRealm$, this.selectedCharacter$]);
}
