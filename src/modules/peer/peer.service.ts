import { Inject, Injectable } from "@nestjs/common";
import { PEER_REPOSITORY } from "src/common/constants";
import { Peer } from "./peer.entity";

@Injectable()
export class PeerService {
    constructor(@Inject(PEER_REPOSITORY) private readonly peerRepository: typeof Peer) {}

    async create(peer: any) {
        return await this.peerRepository.create({
            address: peer.address,
            port: peer.port
        });
    }

    async findByAddressAndPort(address: string, port: number) {
        return await this.peerRepository.findOne({
            where: {
                address,
                port
            }
        });
    }
}