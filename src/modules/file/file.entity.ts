import { BelongsTo, BelongsToMany, Column, DataType, Default, ForeignKey, Model, PrimaryKey, Table, Unique } from "sequelize-typescript";
import { Peer } from "../peer/peer.entity";
import { PeerOnFile } from "../peer/peer_on_file.entity";
import { UUIDV4 } from "sequelize";
import { UUID } from "crypto";
import { User } from "../user/entities/user.entity";

@Table
export class File extends Model<File> {
    @PrimaryKey
    @Default(UUIDV4)
    @Column(DataType.UUID)
    id: UUID;
    
    @Column(DataType.STRING)
    name: string;

    @Column(DataType.INTEGER)
    size: number;

    @Unique
    @Column(DataType.TEXT)
    infoHash: string;

    @ForeignKey(() => User)
    @Column(DataType.UUID)
    userId: UUID;

    @BelongsTo(() => User)
    user: User;

    @BelongsToMany(() => Peer, () => PeerOnFile)
    peers: Peer[];
}