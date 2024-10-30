import { BadRequestException, Inject, Injectable, NotFoundException } from "@nestjs/common";
import { FILE_REPOSITORY, PEER_ON_FILE_REPOSITORY, PEER_REPOSITORY, PeerRole } from "src/common/constants";
import { File } from './file.entity';
import { UploadFileDto } from "./dtos/upload_file.dto";
import { PeerService } from "../peer/peer.service";
import { PeerOnFileService } from "../peer/peer_on_file.service";
import { Peer } from "../peer/peer.entity";
import { PeerOnFile } from "../peer/peer_on_file.entity";
import { UUID } from "crypto";
import { UserService } from "../user/services/user.service";
import { User } from "../user/entities/user.entity";
import { AnnounceDto } from "./dtos/create_peer_on_file.dto";

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

        await this.peerOnFileService.create(existedFile.id, existedPeer.id, PeerRole.SEEDER);

        return existedFile;
    }

    async announce(dto: AnnounceDto) {
        let existedFile = await this.fileRepository.findOne({
            where: {
                infoHash: dto.infoHash
            }
        });

        if (!existedFile) {
            throw new NotFoundException('File không tồn tại')
        }

        if (dto.status === 'start') {
            let existedPeer = await this.peerService.findByAddressAndPort(dto.peerAddress, dto.peerPort);

            if (!existedPeer) {
                existedPeer = await this.peerService.create({
                    address: dto.peerAddress,
                    port: dto.peerPort
                });
            }

            return await this.peerOnFileService.update(existedPeer.id, existedFile.id, PeerRole.LEECHER);
        }

        if (dto.status === 'completed') {
            let existedPeer = await this.peerService.findByAddressAndPort(dto.peerAddress, dto.peerPort);

            if (!existedPeer) {
                existedPeer = await this.peerService.create({
                    address: dto.peerAddress,
                    port: dto.peerPort
                });
            }

            return await this.peerOnFileService.update(existedPeer.id, existedFile.id, PeerRole.SEEDER);
        }

        return null;
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
            return await this.peerOnFileService.create(existedFile.id, existedPeer.id, PeerRole.SEEDER);
        }

        throw new BadRequestException('Announcing failed since your upload has been recorded before');
    }

    async scrape(infoHash: string) {
        const existedFile = await this.fileRepository.findOne({
            where: {
                infoHash
            }
        });

        if (!existedFile) {
            throw new NotFoundException('File không tồn tại');
        }

        const peersOnFile = await this.peerOnFileRepository.findAll({
            where: {
                fileId: existedFile.id,
            },
            attributes: ['role'],
            include: [
                { model: Peer, attributes: ['address', 'port'] }
            ]
        });
        
        return peersOnFile.map(pof => { return { role: pof.role , address: pof.peer.address, port: pof.peer.port } });
    }

    async getSeeders(infoHash: string) {
        const existedFile = await this.fileRepository.findOne({
            where: {
                infoHash
            }
        });

        if (!existedFile) {
            throw new NotFoundException('File không tồn tại');
        }

        const seedersOnFile = await this.peerOnFileRepository.findAll({
            where: {
                fileId: existedFile.id,
                role: PeerRole.SEEDER
            },
            attributes: [],
            include: [
                { model: Peer, attributes: ['address', 'port'] }
            ]
        });
        
        return seedersOnFile.map(sof => sof.peer);
    }

    async unlink(address: string, port: number, infoHash: string) {
        const existedPeer = await this.peerRepository.findOne({
            where: {
                address,
                port
            }
        });

        if (!existedPeer) {
            throw new NotFoundException('Peer không tồn tại');
        }

        const existedFile = await this.fileRepository.findOne({
            where: {
                infoHash
            }
        });

        if (!existedFile) {
            throw new NotFoundException('File không tồn tại');
        }

        await this.peerOnFileRepository.destroy({
            where: {
                peerId: existedPeer.id,
                fileId: existedFile.id
            }
        });
    }
}