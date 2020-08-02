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

import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { Router } from '@angular/router';

import { UserService, UserProfile, Guild } from 'src/app/user/user.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnChanges {
  @Input() profile?: UserProfile;
  @Input() selectedGuild?: Guild;
  @Output() selectedGuildChange = new EventEmitter<Guild>();

  constructor(private readonly router: Router, private readonly userService: UserService) { }

  ngOnChanges() {
    if (this.profile && !this.selectedGuild) {
      this.selectedGuild = this.profile.guilds[0];
      // Emit the automatic selection on the next cycle.
      setTimeout(() => {
        this.selectedGuildChange.emit(this.selectedGuild);
      });
    }
  }

  onGuildSelected(guild: Guild) {
    if (this.selectedGuild?.id !== guild.id) {
      this.selectedGuild = guild;
      this.selectedGuildChange.emit(guild);
    }
  }

  logoutUser() {
    this.userService.logout().subscribe(() => {
      this.router.navigate(['/'], {queryParams: {'refresh': 1}});
    });
  }

  trackByGuildId(index: number, guild: any): string {
    return guild.id;
  }
}
