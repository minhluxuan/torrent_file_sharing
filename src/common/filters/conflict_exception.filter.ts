import { ExceptionFilter, Catch, ArgumentsHost, HttpStatus, ConflictException } from '@nestjs/common';

@Catch(ConflictException)
export class ConflictExceptionFilter implements ExceptionFilter {
    catch(exception: ConflictException, host: ArgumentsHost) {
        const ctx = host.switchToHttp();
        const response = ctx.getResponse();
        const status = HttpStatus.CONFLICT;

        response.status(status).json({
            success: false,
            message: exception.message,
            data: null
        });
    }
}