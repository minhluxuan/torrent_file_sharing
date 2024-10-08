import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { FileModule } from './modules/file/file.module';
import { DatabaseModule } from './database/database.module';
import { PeerModule } from './modules/peer/peer.module';

@Module({
  imports: [FileModule, DatabaseModule, PeerModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
