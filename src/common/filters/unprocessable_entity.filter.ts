import { ArgumentsHost, Catch, ExceptionFilter, HttpStatus, UnauthorizedException, UnprocessableEntityException } from "@nestjs/common";

@Catch(UnprocessableEntityException)
export class UnprocessableEntityExceptionFilter implements ExceptionFilter {
  catch(exception: UnprocessableEntityException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const status = HttpStatus.UNPROCESSABLE_ENTITY;

    response.status(status).json({
      success: false,
      message: exception.message,
      data: null
    });
  }
}