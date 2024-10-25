import { IsString } from "class-validator";

export class StaffLoginDto {
    @IsString({ message: 'Tên đăng nhập phải là chuỗi ký tự' })
    username: string;

    @IsString({ message: 'Mật khẩu phải là chuỗi ký tự' })
    password: string;
}