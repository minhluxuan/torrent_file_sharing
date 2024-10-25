import { BadRequestException, Inject, Injectable } from "@nestjs/common";
import * as bcrypt from 'bcrypt';
import { UUID } from "crypto";
import { JwtService } from '@nestjs/jwt';
import { config } from "dotenv";
import { USER_REPOSITORY } from "src/common/constants";
import { User } from "../entities/user.entity";
import { SignUpDto } from "../dtos/sign_up.dto";

config();

@Injectable()
export class AuthService {
    constructor(
        @Inject(USER_REPOSITORY) private readonly userRepository: typeof User,
        private readonly jwtService: JwtService,
    ) {}

    public async signUp(dto: SignUpDto) {
        const userWithExistedUsername = await this.userRepository.findOne({
            where: {
                username: dto.username
            }
        });

        if (userWithExistedUsername) {
            throw new BadRequestException('Tên đăng nhập đã tồn tại');
        }

        return await this.userRepository.create({
            username: dto.username,
            password: await this.hashPassword(dto.password),
            firstName: dto.firstName,
            lastName: dto.lastName
        });
    }

    public async login(user) {
        const accessTokenPayload = {
            id: user.id,
            agencyId: user.agencyId,
            staffId: user.staffId
        }

        const accessToken = await this.generateAccessToken(accessTokenPayload);
        
        delete user.password;
        return { user, accessToken };
    }

    public async generateAccessToken(payload) {
        const token = await this.jwtService.signAsync(payload);
        return token;
    }

    async validateUser(username: string, enteredPassword: string) {
        const existedUser = await this.userRepository.findOne({
            where: {
                username
            }
        });

        if (!existedUser) {
            return null;
        }

        const passwordMatched: boolean = await this.comparePassword(enteredPassword, existedUser.password);
        if (!passwordMatched) {
            return null;
        }

        const { password, ...result } = existedUser['dataValues'];
        return result;
    }

    private async comparePassword(enteredPassword: string, dbPassword: string) {
        const match = await bcrypt.compare(enteredPassword, dbPassword);
        return match;
    }

    public async hashPassword(password: string) {
        const hash = await bcrypt.hash(password, 10);
        return hash;
    }

    async decodeAccessToken(token: string) {
        return await this.jwtService.verifyAsync(token);
    }
}