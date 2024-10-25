import { ArgumentsHost, Catch, ExceptionFilter, HttpException, HttpStatus } from '@nestjs/common';
import { ConnectionAcquireTimeoutError, ConnectionTimedOutError } from 'sequelize';
import * as child_process from 'child_process';

@Catch(ConnectionAcquireTimeoutError, ConnectionTimedOutError)
export class SequelizeExceptionFilter implements ExceptionFilter {
    catch(exception: ConnectionAcquireTimeoutError | ConnectionTimedOutError, host: ArgumentsHost) {
        const ctx = host.switchToHttp();
        const response = ctx.getResponse();
        const status = exception instanceof ConnectionAcquireTimeoutError || exception instanceof ConnectionTimedOutError
        ? HttpStatus.SERVICE_UNAVAILABLE
        : HttpStatus.INTERNAL_SERVER_ERROR;
        
        console.error('Sequelize error:', exception);

        response.status(status).json({
            success: false,
            message: 'Đã xảy ra lỗi. Vui lòng thử lại',
            data: null,
        });

        if (exception instanceof ConnectionAcquireTimeoutError || exception instanceof ConnectionTimedOutError) {
            this.restartApplication();
        }
    }

    private restartApplication() {
        child_process.exec('pm2 restart api', (error, stdout, stderr) => {
            if (error) {
                console.error(`Failed to restart application: ${stderr}`);
                return;
            }
            console.log(`Application restarted successfully: ${stdout}`);
        });
    }
}
