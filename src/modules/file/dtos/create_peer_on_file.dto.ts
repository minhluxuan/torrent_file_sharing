export class AnnounceDto {
    infoHash: string;
    peerAddress: string;
    peerPort: number;
    status: 'start' | 'stop' | 'completed'
}