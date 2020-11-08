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

import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {BrowserModule} from '@angular/platform-browser';
import {HttpClientModule} from '@angular/common/http';
import {MatDialogModule} from '@angular/material/dialog';

import {RouterModule} from '@angular/router';

import {EventsModule} from 'src/app/events/events.module';
import {AppCommonModule} from '../common/common.module';

import {GuildProfileComponent} from './guild-profile.component';
import {GuildService} from './guild.service';
import {GuildEventTableModule} from './event-table/event-table.module';

@NgModule({
  declarations: [GuildProfileComponent],
  imports: [
    AppCommonModule,
    BrowserModule,
    CommonModule,
    EventsModule,
    GuildEventTableModule,
    HttpClientModule,
    MatDialogModule,
    RouterModule,
  ],
  exports: [GuildProfileComponent],
  providers: [GuildService],
})
export class GuildModule {}
