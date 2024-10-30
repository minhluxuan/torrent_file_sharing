import { BadRequestException, Body, Controller, Get, HttpStatus, NotFoundException, Param, Post, Query, Req, Res, UseGuards } from "@nestjs/common";
import { FileService } from "./file.service";
import { UploadFileDto } from "./dtos/upload_file.dto";
import { AnnounceDto } from "./dtos/create_peer_on_file.dto";
import { JwtAuthGuard } from "src/common/guards/authenticate.guard";
import { PeerRole } from "src/common/constants";
import { PeerOnFileService } from "../peer/peer_on_file.service";
import { UnlinkDto } from "./dtos/unlink.dto";

@Controller('file')
export class FileController {
    constructor(
        private readonly fileService: FileService,
        private readonly peerOnFileService: PeerOnFileService
    ) {}

    // @UseGuards(JwtAuthGuard)
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

    // @UseGuards(JwtAuthGuard)
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
    async announce(@Body() announceDto: AnnounceDto, @Res() res) {
        try {
            await this.fileService.announce(announceDto);
            return res.status(HttpStatus.CREATED).json({
                success: true,
                message: 'Announce successfully',
                data: null
            }); 
        } catch (error) {
            console.log(error);
            
            if (error instanceof NotFoundException) {
                return res.status(HttpStatus.NOT_FOUND).json({
                    success: false,
                    message: error.message,
                    data: null
                });
            }

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

    @Get('scrape/:infoHash')
    async scrape(@Param('infoHash') infoHash: string, @Res() res) {
        try {
            const seeders = await this.fileService.scrape(infoHash);
            return res.status(HttpStatus.OK).json({
                success: true,
                message: 'Get seeders successfully',
                data: seeders
            });
        } catch (error) {
            console.log(error);
            
            if (error instanceof NotFoundException) {
                return res.status(HttpStatus.NOT_FOUND).json({
                    success: false,
                    message: error.message,
                    data: null
                });
            }

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

    @Get('seeders/get/:infoHash')
    async getSeeders(@Param('infoHash') infoHash: string, @Res() res) {
        try {
            const seeders = await this.fileService.getSeeders(infoHash);
            return res.status(HttpStatus.OK).json({
                success: true,
                message: 'Get seeders successfully',
                data: seeders
            });
        } catch (error) {
            console.log(error);
            
            if (error instanceof NotFoundException) {
                return res.status(HttpStatus.NOT_FOUND).json({
                    success: false,
                    message: error.message,
                    data: null
                });
            }

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

    @Post('unlink')
    async unlink(@Body() dto: UnlinkDto, @Res() res) {
        try {
            await this.fileService.unlink(dto.address, dto.port, dto.infoHash);
            return res.status(HttpStatus.OK).json({
                success: true,
                message: 'Unlink successfully',
                data: null
            });
        } catch (error) {
            console.log(error);
            
            if (error instanceof NotFoundException) {
                return res.status(HttpStatus.NOT_FOUND).json({
                    success: false,
                    message: error.message,
                    data: null
                });
            }

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