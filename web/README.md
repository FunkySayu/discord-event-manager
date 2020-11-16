# Discord event manager's UI

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 10.0.4.

## Development server

Two development servers exist:
 - run `ng serve` in the `web` to only run the UI, auto-reloading on file modification. This does not integrate with any backend.
 - run `bin/frontend` in the root directory to run a lightweight version of the bot integrating with its storage.

## Style guide

### Resource naming

HTTP routes should follow the Google Cloud API resource naming standard:
 - https://cloud.google.com/apis/design/resource_names
 - https://cloud.google.com/apis/design/standard_methods
 - https://cloud.google.com/apis/design/custom_methods
 
### TypeScript

Use `gts` to check for style compliance and auto-format:
 - https://github.com/google/gts
 
## Troubleshooting

### Compilation issue

If the `bin/frontend` crashes on build, follow this procedure:
 - ensure your packages are well installed: `cd web && npm install`
 - ensure your Angular CLI is at 10.0.4: `sudo npm i --global @angular/cli@10.0.4`

## Angular cheat sheet

### Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

### Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

### Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

### Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

### Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
