import { BadRequestException, Inject, Injectable, NotFoundException } from "@nestjs/common";
import { FILE_REPOSITORY, PEER_ON_FILE_REPOSITORY, PEER_REPOSITORY } from "src/common/constants";
import { File } from './file.entity';
import { UploadFileDto } from "./dtos/upload_file.dto";
import { PeerService } from "../peer/peer.service";
import { PeerOnFileService } from "../peer/peer_on_file.service";
import { Peer } from "../peer/peer.entity";
import { PeerOnFile } from "../peer/peer_on_file.entity";
import { UUID } from "crypto";
import { UserService } from "../user/services/user.service";
import { User } from "../user/entities/user.entity";

@Injectable()
export class FileService {
    constructor(
        @Inject(FILE_REPOSITORY) private readonly fileRepository: typeof File,
        private readonly peerService: PeerService,
        private readonly peerOnFileService: PeerOnFileService,
        @Inject(PEER_REPOSITORY) private readonly peerRepository: typeof Peer,
        @Inject(PEER_ON_FILE_REPOSITORY) private readonly peerOnFileRepository: typeof PeerOnFile,
        private readonly userService: UserService
    ) {}

    async search(infoHash: string) {
        if (infoHash) {
            return await this.fileRepository.findAll({
                where: {
                    infoHash
                },
                include: [
                    { 
                        model: Peer, through: { attributes: [] }, 
                        attributes: ['address', 'port']
                    },
                    { 
                        model: User,
                        attributes: ['firstName', 'lastName']
                    }
                ]
            });
        }

        return await this.fileRepository.findAll({
            include: [
                { 
                    model: Peer, through: { attributes: [] }, 
                    attributes: ['address', 'port']
                },
                { 
                    model: User,
                    attributes: ['firstName', 'lastName']
                }
            ]
        });
    }

    async create(dto: UploadFileDto, userId: UUID) {
        if (userId) {
            const existedUser = await this.userService.checkExist(userId);
            if (!existedUser) {
                throw new NotFoundException('Người dùng không tồn tại');
            }
        }

        let existedFile = await this.fileRepository.findOne({
            where: {
                infoHash: dto.infoHash
            }
        });

        if (!existedFile) {
            existedFile = await this.fileRepository.create({
                infoHash: dto.infoHash,
                name: dto.name,
                size: dto.size,
                userId: userId
            });
        }

        let existedPeer = await this.peerService.findByAddressAndPort(dto.peerAddress, dto.peerPort);

        if (!existedPeer) {
            existedPeer = await this.peerService.create({
                address: dto.peerAddress,
                port: dto.peerPort
            });
        }

        await this.peerOnFileService.create(existedFile.id, existedPeer.id);

        return existedFile;
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
                infoHash: infoHash
            }
        });

        if (!existedFile) {
            existedFile = await this.fileRepository.create({
                infoHash: infoHash,
                name: fileName,
                size: fileSize
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