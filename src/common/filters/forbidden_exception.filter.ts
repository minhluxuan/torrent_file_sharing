import { ArgumentsHost, Catch, ExceptionFilter, ForbiddenException, HttpStatus } from "@nestjs/common";

@Catch(ForbiddenException)
export class ForbiddenExceptionFilter implements ExceptionFilter {
  catch(exception: ForbiddenException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const status = HttpStatus.FORBIDDEN;

    response.status(status).json({
      success: false,
      message: "Người dùng không được phép truy cập tài nguyên này",
      data: null
    });
  }
}