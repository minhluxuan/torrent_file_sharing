import { Inject, Injectable } from "@nestjs/common";
import { USER_REPOSITORY } from "src/common/constants";
import { User } from "../entities/user.entity";
import { UUID } from "crypto";

@Injectable()
export class UserService {
    constructor(@Inject(USER_REPOSITORY) private readonly userRepository: typeof User) {}

    async create() {
        return this.userRepository.create({});
    }

    async findById(id: UUID) {
        return this.userRepository.findByPk(id);
    }

    async checkExist(id: UUID) {
        const existedUser = await this.userRepository.findByPk(id, {
            attributes: ['id']
        });

        if (existedUser) {
            return true;
        }

        return false;
    }
}