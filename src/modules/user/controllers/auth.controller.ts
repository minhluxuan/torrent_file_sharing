import { BadRequestException, Body, Controller, HttpStatus, InternalServerErrorException, Post, Req, Res, UseGuards, UsePipes } from "@nestjs/common";
import { UserService } from "../services/user.service";
import { AuthService } from "../services/auth.service";
import { AuthGuard } from "@nestjs/passport";
import { StaffLoginDto } from "../dtos/login.dto";
import { Response } from "src/modules/response/response.entity";
import { ValidateInputPipe } from "src/common/pipes/validate.pipe";
import { SignUpDto } from "../dtos/sign_up.dto";

@Controller('auth')
export class AuthController {
    constructor(
        private readonly response: Response,
        private readonly authService: AuthService
    ) {}

    @Post('signup')
    async signUp(@Body() dto: SignUpDto, @Res() res) {
        try {
            console.log(dto);
            const createdUser = await this.authService.signUp(dto);
            this.response.initResponse(true, 'Sign up successfully', createdUser);
            return res.status(HttpStatus.CREATED).json(this.response);
        } catch (error) {
            if (error instanceof BadRequestException) {
                this.response.initResponse(false, error.message, null);
                return res.status(HttpStatus.BAD_REQUEST).json(this.response);
            }

            console.log(error);
            this.response.initResponse(false, "Đã xảy ra lỗi. Vui lòng thử lại", null);
            return res.status(HttpStatus.INTERNAL_SERVER_ERROR).json(this.response);
        }
    }

    @UseGuards(AuthGuard('local'))
    @UsePipes(ValidateInputPipe)
    @Post('login')
    async logIn(@Req() req, @Body() dto: StaffLoginDto, @Res() res) {
        try {
            const { user: { password, ...result }, accessToken } =  await this.authService.login(req.user);
            if (!accessToken) {
                throw new InternalServerErrorException();
            }

            res.cookie('sid', accessToken, {
                httpOnly: false,
                secure: true,
                maxAge: 2 * 60 * 60 * 1000,
                sameSite: 'none',
            });

            this.response.initResponse(true, "Đăng nhập thành công", {...result, accessToken});
            return res.status(HttpStatus.OK).json(this.response);
        } catch (error) {
            console.log(error);
            this.response.initResponse(false, "Đã xảy ra lỗi. Vui lòng thử lại", null);
            return res.status(HttpStatus.INTERNAL_SERVER_ERROR).json(this.response);
        }
    }
}