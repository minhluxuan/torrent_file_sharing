import { UUID } from "crypto";
import { AutoIncrement, BelongsTo, BelongsToMany, Column, DataType, ForeignKey, Model, PrimaryKey, Table } from "sequelize-typescript";
import { Peer } from "./peer.entity";
import { File } from "../file/file.entity";
import { PeerRole } from "src/common/constants";

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

    @Column({
        type: DataType.ENUM(...Object.values(PeerRole))
    })
    role: PeerRole;

    @BelongsTo(() => Peer)
    peer: Peer;
}