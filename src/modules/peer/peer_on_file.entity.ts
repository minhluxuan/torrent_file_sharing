import { UUID } from "crypto";
import { AutoIncrement, Column, DataType, ForeignKey, Model, PrimaryKey, Table } from "sequelize-typescript";
import { Peer } from "./peer.entity";
import { File } from "../file/file.entity";

@Table
export class PeerOnFile extends Model<PeerOnFile> {
    @PrimaryKey
    @AutoIncrement
    @Column(DataType.INTEGER)
    id: number;

    @ForeignKey(() => File)
    @Column(DataType.UUID)
    fileId: UUID;

    @ForeignKey(() => Peer)
    @Column(DataType.UUID)
    peerId: UUID;
}