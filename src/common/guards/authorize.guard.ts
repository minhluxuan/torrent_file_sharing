import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Observable } from 'rxjs';

@Injectable()
export class AuthorizeGuard implements CanActivate {
	constructor(private reflector: Reflector) {}

	canActivate(
		context: ExecutionContext,
	): boolean | Promise<boolean> | Observable<boolean> {
		const roles = this.reflector.get<string[]>('roles', context.getHandler());
		if (!roles) {
			return true;
		}
		const request = context.switchToHttp().getRequest();
		return this.matchRoles(roles, request.user.roles ? request.user.roles : []);
	}
	
	matchRoles(roles: string[], userRoles: string[]): boolean {
		for (const ur of userRoles) {
			if (roles.includes(ur)) {
				return true;
			}
		}

		return false;
	}
}
