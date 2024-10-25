import { ArgumentsHost, BadRequestException, Catch, ExceptionFilter, HttpStatus } from "@nestjs/common";

@Catch(BadRequestException)
export class BadRequestExceptionFilter implements ExceptionFilter {
  catch(exception: BadRequestException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const status = HttpStatus.BAD_REQUEST;

    console.log(exception);

    response.status(status).json({
      success: false,
      message: exception.message,
      data: null
    });
  }
}