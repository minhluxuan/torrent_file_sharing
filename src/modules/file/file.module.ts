import { Module } from '@nestjs/common';
import { filesProviders } from './file.provider';
import { FileController } from './file.controller';
import { FileService } from './file.service';
import { PeerModule } from '../peer/peer.module';
import { PeerOnFileService } from '../peer/peer_on_file.service';
import { UserModule } from '../user/user.module';

@Module({
    imports: [FileModule, PeerModule, UserModule],
    providers: [...filesProviders, FileService, PeerOnFileService],
    controllers: [FileController],
    exports: [...filesProviders, FileService, PeerOnFileService]
})
export class FileModule {}
