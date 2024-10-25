import { ArgumentsHost, Catch, ExceptionFilter, HttpStatus, UnauthorizedException } from "@nestjs/common";

@Catch(UnauthorizedException)
export class UnauthorizedExceptionFilter implements ExceptionFilter {
  catch(exception: UnauthorizedException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const status = HttpStatus.UNAUTHORIZED;

    response.status(status).json({
      success: false,
      message: exception.message,
      data: null
    });
  }
}