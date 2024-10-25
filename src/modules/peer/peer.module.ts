import { Module } from '@nestjs/common';
import { peersProviders } from './peer.provider';
import { PeerService } from './peer.service';
import { PeerOnFileService } from './peer_on_file.service';

@Module({
    imports: [PeerModule],
    providers: [...peersProviders, PeerService, PeerOnFileService],
    controllers: [],
    exports: [...peersProviders, PeerService, PeerOnFileService]
})
export class PeerModule {}
