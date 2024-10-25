import { ArgumentMetadata, BadRequestException, UnprocessableEntityException, ValidationPipe } from "@nestjs/common";
import { plainToClass } from "class-transformer";
import { validate, ValidationError } from "class-validator";

export class ValidateSearchingInputPipe<T extends object> extends ValidationPipe {
	constructor(private readonly options: { new(): T }) {
		super();
	}

	async transform(value: any, metadata: ArgumentMetadata) {
		if (metadata.type === 'body') {
			const criteria = value.criteria as any[];
			if (criteria == null) {
				value.criteria = [];
				return value;
			}
			
			for (const criterion of criteria) {
				const { field, operator, value: fieldValue } = criterion;
				if (field.includes('.')) {
					continue;
				}

				if (!this.isOperatorValidForType(field, operator)) {
					throw new UnprocessableEntityException(`Toán tử "${operator}" không tương thích với trường "${field}" với giá trị "${fieldValue}".`);
				}

				const partialEntity = plainToClass(this.options, { [field]: fieldValue });

				delete (partialEntity as any).lang;

				const errors = await validate(partialEntity, { whitelist: true, forbidNonWhitelisted: true });

				if (errors.length > 0) {
					throw new UnprocessableEntityException(this.formatErrors(errors));
				}
			}
		}

		return value;
	}

	private isOperatorValidForType(field: string, operator: string): boolean {
		const entity = new this.options();
		const fieldType = Reflect.getMetadata('design:type', entity, field);
        console.log(field);
        console.log(fieldType);
		switch (fieldType) {
			case String:
			  	return ['~', '!~', '=', '!=', 'isSet', 'isNotSet'].includes(operator);
			case Number:
			  	return ['=', '!=', '<', '<=', '>', '>=', 'isSet', 'isNotSet'].includes(operator);
			case Boolean:
			  	return ['=', '!=', 'isSet', 'isNotSet'].includes(operator);
			case Date:
				return ['=', '!=', '<', '<=', '>', '>=', 'isSet', 'isNotSet'].includes(operator);
			default:
			  	return ['isSet', 'isNotSet'].includes(operator);
		}
	}

	private formatErrors(errors: ValidationError[]): string {
		return errors.map(err => Object.values(err.constraints || {}).join(', ')).join(', ');
	}
}