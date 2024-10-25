import { Strategy } from 'passport-local';
import { PassportStrategy } from '@nestjs/passport';
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { AuthService } from '../services/auth.service';

@Injectable()
export class LocalStrategy extends PassportStrategy(Strategy) {
    constructor(
        private readonly authService: AuthService
    ) {
        super({
			usernameField: 'username',
			passwordField: 'password',
        });
    }

    async validate(identifier: string, password: string): Promise<any>{
        const user = await this.authService.validateUser(identifier, password);
        if (!user) {
         	throw new UnauthorizedException('Invalid user credentials');
        }
        
        return user;
    }
}