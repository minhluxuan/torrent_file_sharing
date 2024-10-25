import { UUID } from "crypto";
import { UUIDV4 } from "sequelize";
import { BelongsToMany, Column, DataType, Default, Model, PrimaryKey, Table, Unique } from "sequelize-typescript";
import { File } from "../file/file.entity";
import { PeerOnFile } from "./peer_on_file.entity";

@Table
export class Peer extends Model<Peer> {
    @PrimaryKey
    @Default(UUIDV4)
    @Column(DataType.UUID)
    id: UUID;

    @Column(DataType.STRING)
    address: string;

    @Column(DataType.INTEGER)
    port: number;

    @BelongsToMany(() => File, () => PeerOnFile)
    files: File[];
}