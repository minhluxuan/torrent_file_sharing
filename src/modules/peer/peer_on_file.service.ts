import { ConflictException, Inject, Injectable, NotFoundException } from "@nestjs/common";
import { PeerOnFile } from "./peer_on_file.entity";
import { PEER_ON_FILE_REPOSITORY, PEER_REPOSITORY } from "src/common/constants";
import { UUID } from "crypto";
import { Peer } from "./peer.entity";
import { PeerService } from "./peer.service";

@Injectable()
export class PeerOnFileService {
    constructor(
        @Inject(PEER_ON_FILE_REPOSITORY) private readonly peerOnFileRepository: typeof PeerOnFile,
        @Inject(PEER_REPOSITORY) private readonly peerRepository: typeof Peer,
        private readonly peerService: PeerService
    ) {}

    async create(fileId: UUID, peerId: UUID) {
        const existedPair = await this.peerOnFileRepository.findAll({
            where: {
                fileId,
                peerId
            }
        });

        if (existedPair && existedPair.length > 0) {
            throw new ConflictException('Pair has been existed');
        }

        return await this.peerOnFileRepository.create({
            fileId,
            peerId
        });
    }
}