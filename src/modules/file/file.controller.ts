import { BadRequestException, Body, Controller, Get, HttpStatus, Post, Query, Req, Res, UseGuards } from "@nestjs/common";
import { FileService } from "./file.service";
import { UploadFileDto } from "./dtos/upload_file.dto";
import { CreatePeerOnFileDto } from "./dtos/create_peer_on_file.dto";
import { JwtAuthGuard } from "src/common/guards/authenticate.guard";

@Controller('file')
export class FileController {
    constructor(
        private readonly fileService: FileService
    ) {}

    @UseGuards(JwtAuthGuard)
    @Get('fetch')
    async search(@Res() res, @Query('info_hash') infoHash: string) {
        try {
            const files = await this.fileService.search(infoHash);
            return res.status(HttpStatus.OK).json({
                success: true,
                message: 'Get file successfully',
                data: files
            });
        } catch (error) {
            console.log(error);
            return res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
                success: false,
                message: 'Internal server error',
                data: null
            });
        }
    }

    @UseGuards(JwtAuthGuard)
    @Post('publish')
    async upload(@Req() req, @Body() uploadFileDto: UploadFileDto, @Res() res) {
        try {
            if (req.user) {
                const createdFile = await this.fileService.create(uploadFileDto, req.user.id);
                return res.status(HttpStatus.CREATED).json({
                    success: true,
                    message: 'Upload file successfully',
                    data: createdFile
                });
            }
            
            const createdFile = await this.fileService.create(uploadFileDto, null);
            return res.status(HttpStatus.CREATED).json({
                success: true,
                message: 'Upload file successfully',
                data: createdFile
            });
        } catch (error) {
            console.log(error);
            
            if (error instanceof BadRequestException) {
                return res.status(HttpStatus.BAD_REQUEST).json({
                    success: false,
                    message: error.message,
                    data: null
                });
            }

            return res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
                success: false,
                message: 'Internal server error',
                data: null
            });
        }
    }

    @Post('/peers/announce')
    async createPeerOnFile(@Body() createPeerOnFileDto: CreatePeerOnFileDto, @Res() res) {
        try {
            const createdPOF = await this.fileService.createPOFByInfoHashAndPeerAddress(createPeerOnFileDto.infoHash, createPeerOnFileDto.fileName, createPeerOnFileDto.fileSize, createPeerOnFileDto.peerAddress, createPeerOnFileDto.peerPort);
            return res.status(HttpStatus.CREATED).json({
                success: true,
                message: 'Announce successfully',
                data: createdPOF
            }); 
        } catch (error) {
            console.log(error);
            
            if (error instanceof BadRequestException) {
                return res.status(HttpStatus.BAD_REQUEST).json({
                    success: false,
                    message: error.message,
                    data: null
                });
            }

            return res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
                success: false,
                message: 'Internal server error',
                data: null
            });
        }
    }
}