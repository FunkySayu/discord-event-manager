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

import { Component, Input } from '@angular/core';

const DISCORD_CDN = 'https://cdn.discordapp.com'

@Component({
  selector: 'discord-icon',
  templateUrl: './icon.component.html',
  styleUrls: ['./icon.component.scss']
})
export class IconComponent {
  @Input() type?: 'icons'|'avatars';
  @Input() id?: string;
  @Input() icon?: string;

  get src(): string|undefined {
    if (!this.type || !this.id || !this.icon) {
      return;
    }
    return `${DISCORD_CDN}/${this.type}/${this.id}/${this.icon}.png`;
  }
}
