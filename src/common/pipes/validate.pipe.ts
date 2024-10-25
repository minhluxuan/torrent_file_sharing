import {
  Injectable,
  ArgumentMetadata,
  BadRequestException,
  ValidationPipe,
  UnprocessableEntityException,
} from '@nestjs/common';

import { ValidationError, validate } from 'class-validator';
import {plainToClass} from 'class-transformer';
import 'reflect-metadata';

@Injectable()
export class ValidateInputPipe extends ValidationPipe {
	public async transform(value: any, metadata: ArgumentMetadata) {
		try {
			return await super.transform(value, metadata);
		} catch (e) {
			if (e instanceof BadRequestException) {
				throw new UnprocessableEntityException(
					this.handleError(e.getResponse()),
				);
			}
		}
	}

	private handleError(errors: any) {
		if (typeof errors === 'string') {
			return errors;
		} else if (Array.isArray(errors.message)) {
			return errors.message[0];
		} else {
			return Object.values(errors.message)[0];
		}
	}
}