import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { FileModule } from './modules/file/file.module';
import { DatabaseModule } from './database/database.module';
import { PeerModule } from './modules/peer/peer.module';
import { UserModule } from './modules/user/user.module';
import { appProviders } from './app.provider';

@Module({
  imports: [FileModule, DatabaseModule, PeerModule, UserModule],
  controllers: [AppController],
  providers: [AppService, ...appProviders],
})
export class AppModule {}
