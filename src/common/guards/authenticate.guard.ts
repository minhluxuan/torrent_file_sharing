import { Injectable, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { AuthService } from 'src/modules/user/services/auth.service';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
	constructor(
		private readonly authService : AuthService,
	) {
		super();
	};

    async canActivate(context: ExecutionContext): Promise<boolean> {
        const request = context.switchToHttp().getRequest();

        let token: string = request.headers['authorization'];
        if (!token) {
			throw new UnauthorizedException('Please login to continue');
        }

        if (token.startsWith('Bearer ')) {
			token = token.replace('Bearer ', '');
		}

		try {
			const payload = await this.authService.decodeAccessToken(token);
			request.user = payload;
			return true;
		} catch (err) {
			throw new UnauthorizedException('Invalid token');
		}
    }
}
