import {Injectable} from '@angular/core';
import {CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router} from '@angular/router';
import { UserService } from './user.service';
import {firstValueFrom} from 'rxjs';

interface IsAuthenticatedGuardConfig {
    fallback?: string[];
}

@Injectable({
    providedIn: 'root'
})
export class IsAuthenticatedGuard implements CanActivate {
    constructor(private readonly userService: UserService, private readonly router: Router) {
    }

    async canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
        const config = IsAuthenticatedGuard.readConfig(state);

        const isAuthenticated = await firstValueFrom(this.userService.isAuthenticated());
        if (isAuthenticated) {
            return true;
        }
        return this.router.createUrlTree(config.fallback ?? ['']);
    }

    static readConfig(state: RouterStateSnapshot): IsAuthenticatedGuardConfig {
        if (!state.root.data.isAuthenticatedGuardConfig) {
            return {};
        }
        return state.root.data.isAuthenticatedGuardConfig as IsAuthenticatedGuardConfig;
    }
}