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

/** Represents a timestamp record returned by the server. */
export type Timestamp = string;

/** Enumerator over all supported timezones within the application. */
export enum Timezone {
  UTC = 'UTC',
  EUROPE_PARIS = 'Europe/Paris',
}

/** List of all possible values for the timezones in the application. */
export const ALL_TIMEZONES = [Timezone.UTC, Timezone.EUROPE_PARIS];

/** Human readable names for each timezones. */
export const TIMEZONE_NAMES: Record<Timezone, string> = {
  [Timezone.UTC]: 'UTC',
  [Timezone.EUROPE_PARIS]: 'Europe/Paris',
};

/** Naive transformation of a date to a timestamp. Note this does NOT take into consideration timezone! */
export function naiveConvertDateToTimestamp(date: Date): Timestamp {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDay()} ${date.getHours()}:${date.getMinutes()}:00`;
}
