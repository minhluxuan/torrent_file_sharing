export class CreatePeerOnFileDto {
    infoHash: string;
    fileName: string;
    fileSize: number;
    peerAddress: string;
    peerPort: number;
}