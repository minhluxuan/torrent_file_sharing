import { PEER_ON_FILE_REPOSITORY, PEER_REPOSITORY } from 'src/common/constants';
import { Peer } from './peer.entity';
import { PeerOnFile } from './peer_on_file.entity';

export const peersProviders = [{
    provide: PEER_REPOSITORY,
    useValue: Peer
}, {
    provide: PEER_ON_FILE_REPOSITORY,
    useValue: PeerOnFile
}]