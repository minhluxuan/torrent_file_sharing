import { ArgumentsHost, Catch, ExceptionFilter, HttpStatus, NotFoundException } from "@nestjs/common";

@Catch(NotFoundException)
export class NotFoundExceptionFilter implements ExceptionFilter {
  catch(exception: NotFoundException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const status = HttpStatus.NOT_FOUND;

    response.status(status).json({
      success: false,
      message: exception.message,
      data: null
    });
  }
}