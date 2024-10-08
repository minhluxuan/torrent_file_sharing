import { BadRequestException, Inject, Injectable } from "@nestjs/common";
import { FILE_REPOSITORY, PEER_ON_FILE_REPOSITORY, PEER_REPOSITORY } from "src/common/constants";
import { File } from './file.entity';
import { UploadFileDto } from "./dtos/upload_file.dto";
import { PeerService } from "../peer/peer.service";
import { PeerOnFileService } from "../peer/peer_on_file.service";
import { Peer } from "../peer/peer.entity";
import { PeerOnFile } from "../peer/peer_on_file.entity";

@Injectable()
export class FileService {
    constructor(
        @Inject(FILE_REPOSITORY) private readonly fileRepository: typeof File,
        private readonly peerService: PeerService,
        private readonly peerOnFileService: PeerOnFileService,
        @Inject(PEER_REPOSITORY) private readonly peerRepository: typeof Peer,
        @Inject(PEER_ON_FILE_REPOSITORY) private readonly peerOnFileRepository: typeof PeerOnFile,
    ) {}

    async search(hashInfo: string) {
        if (hashInfo) {
            return await this.fileRepository.findAll({
                where: {
                    hashInfo
                },
                include: [
                    {model: Peer, through: { attributes: []}}
                ]
            });
        }

        return await this.fileRepository.findAll();
    }

    async create(dto: UploadFileDto) {
        const existedFile = await this.fileRepository.findOne({
            where: {
                hashInfo: dto.hashInfo
            }
        });

        if (existedFile) {
            throw new BadRequestException('File has been existed');
        }

        let existedPeer = await this.peerService.findByAddressAndPort(dto.peerAddress, dto.peerPort);

        if (!existedPeer) {
            existedPeer = await this.peerService.create({
                address: dto.peerAddress,
                port: dto.peerPort
            });
        }

        const createdFile = await this.fileRepository.create({
            hashInfo: dto.hashInfo,
            name: dto.name,
            trackerUrl: 'http://localhost:3000',
            size: dto.size
        });

        await this.peerOnFileService.create(createdFile.id, existedPeer.id);

        return createdFile;
    }

    async createPOFByInfoHashAndPeerAddress(infoHash: string, fileName: string, fileSize: number, peerAddress: string, peerPort: number) {
        let existedPeer = await this.peerRepository.findOne({
            where: {
                address: peerAddress,
                port: peerPort
            }
        });

        if (!existedPeer) {
            existedPeer = await this.peerService.create({
                address: peerAddress,
                port: peerPort
            });
        }

        let existedFile = await this.fileRepository.findOne({
            where: {
                hashInfo: infoHash
            }
        });

        if (!existedFile) {
            existedFile = await this.fileRepository.create({
                hashInfo: infoHash,
                name: fileName,
                size: fileSize,
                trackerUrl: 'http://localhost:3000'
            });
        }

        if (!await this.peerOnFileRepository.findOne({
            where: {
                fileId: existedFile.id,
                peerId: existedPeer.id
            }
        })) {
            return await this.peerOnFileService.create(existedFile.id, existedPeer.id);
        }

        throw new BadRequestException('Announcing failed since your upload has been recorded before');
    }
}