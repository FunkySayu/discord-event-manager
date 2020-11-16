/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';

import {StylesDemoComponent} from './demo/styles/styles.component';
import {DemoModule} from './demo/demo.module';
import {LandingComponent} from './landing/landing.component';
import {LandingModule} from './landing/landing.module';
import {GuildProfileComponent} from './guild/guild-profile.component';
import {GuildModule} from './guild/guild.module';

const routes: Routes = [
  {path: 'demo/styles-palette', component: StylesDemoComponent},
  {path: 'guild/:guildId', component: GuildProfileComponent},
  {path: '', component: LandingComponent},
];

@NgModule({
  imports: [DemoModule, GuildModule, LandingModule, RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
