import { Module } from '@nestjs/common';
import { DatabaseModule } from 'src/database/database.module';
import { userProviders } from './user.provider';
import { AuthController } from './controllers/auth.controller';
import { UserService } from './services/user.service';
import { AuthService } from './services/auth.service';
import { JwtModule } from '@nestjs/jwt';
import { config } from 'dotenv';
import { LocalStrategy } from './strategies/local.strategy';
import { ResponseModule } from '../response/response.module';

config();

@Module({
    imports: [
        DatabaseModule,
        JwtModule.register({
            secret: process.env.JWT_ACCESS_KEY,
            signOptions: { expiresIn: process.env.ACCESS_TOKEN_EXPIRATION },
        }),
        ResponseModule
    ],
    providers: [
        ...userProviders,
        UserService,
        AuthService,
        LocalStrategy
    ],
    controllers: [AuthController],
    exports: [UserService, AuthService, ...userProviders],
})
export class UserModule {}
