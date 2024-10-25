import { UUID } from "crypto";
import { UUIDV4 } from "sequelize";
import { AllowNull, Column, DataType, Default, Model, PrimaryKey, Table } from "sequelize-typescript";

@Table
export class User extends Model<User> {
    @PrimaryKey
    @Default(UUIDV4)
    @Column(DataType.UUID)
    id: UUID;

    @AllowNull(false)
    @Column(DataType.STRING)
    username: string;

    @AllowNull(false)
    @Column(DataType.STRING)
    password: string;

    @AllowNull(false)
    @Column(DataType.STRING)
    firstName: string;

    @AllowNull(false)
    @Column(DataType.STRING)
    lastName: string;
}