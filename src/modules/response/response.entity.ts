import { Injectable } from "@nestjs/common";

@Injectable()
export class Response {
    private success: boolean;
    private message: string;
    private data: any;

    constructor(success: boolean, message: string, data: any) {
        this.success = success;
        this.message = message;
        this.data = data;
    }

    public initResponse(success: boolean, message: string, data: any) {
        this.success = success;
        this.message = message;
        this.data = data;
    }
}