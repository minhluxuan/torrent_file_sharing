import { APP_FILTER } from './common/constants';
import { BadRequestExceptionFilter } from './common/filters/bad_request_exception.filter';
import { ConflictExceptionFilter } from './common/filters/conflict_exception.filter';
import { ForbiddenExceptionFilter } from './common/filters/forbidden_exception.filter';
import { NotFoundExceptionFilter } from './common/filters/not_found_exception.filter';
import { SequelizeExceptionFilter } from './common/filters/sequelize_connection_acquire_timeout_error.filter';
import { UnauthorizedExceptionFilter } from './common/filters/unauthorized.filter';
import { UnprocessableEntityExceptionFilter } from './common/filters/unprocessable_entity.filter';

export const appProviders = [{
    provide: APP_FILTER,
    useClass: ConflictExceptionFilter,
}, {
    provide: APP_FILTER,
    useClass: BadRequestExceptionFilter,
}, {
    provide: APP_FILTER,
    useClass: UnauthorizedExceptionFilter,
},
{
    provide: APP_FILTER,
    useClass: ForbiddenExceptionFilter,
},
{
    provide: APP_FILTER,
    useClass: UnprocessableEntityExceptionFilter,
},
{
    provide: APP_FILTER,
    useClass: NotFoundExceptionFilter,
}, {
    provide: APP_FILTER,
    useClass: SequelizeExceptionFilter,
}];