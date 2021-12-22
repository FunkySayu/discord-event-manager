import {Injectable} from '@angular/core';
import {CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router} from '@angular/router';
import { UserService } from './user.service';
import { firstValueFrom } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class RedirectToFirstGuildGuard implements CanActivate {
    constructor(private readonly userService: UserService, private readonly router: Router) {
    }

    async canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
        const isAuthenticated = await firstValueFrom(this.userService.isAuthenticated());
        if (!isAuthenticated) {
            return true;
        }
        const profile = await firstValueFrom(this.userService.getUserProfile());
        if (profile?.guilds?.[0]?.guild?.id) {
            return this.router.createUrlTree(['guild', profile.guilds[0].guild.id])
        }
        return true;
    }
}