import { Sequelize } from 'sequelize-typescript'
import { SEQUELIZE, DEVELOPMENT, TEST, PRODUCTION } from '../common/constants';
import { databaseConfig } from './database.config';
import { File } from 'src/modules/file/file.entity';
import { PeerOnFile } from 'src/modules/peer/peer_on_file.entity';
import { Peer } from 'src/modules/peer/peer.entity';
import { User } from 'src/modules/user/entities/user.entity';

export const databaseProviders = [
  {
    provide: SEQUELIZE,
    useFactory: async () => {
      let config;
      switch (process.env.NODE_ENV) {
        case DEVELOPMENT:
          config = databaseConfig.development;
          break;
        case TEST:
          config = databaseConfig.test;
          break;
        case PRODUCTION:
          config = databaseConfig.production;
          break;
        default:
          config = databaseConfig.development;
      }
      const sequelize = new Sequelize(config);
      sequelize.addModels([File, PeerOnFile, Peer, User]);
      await sequelize.sync();

      try {
        await sequelize.authenticate();
        console.log('Connection has been established successfully');
        await sequelize.sync();
        console.log('Database synchronized successfully');
      } catch (error) {
        console.error('Unable to connect to the database:', error);
      }
      
      return sequelize;
    },
  },
];
