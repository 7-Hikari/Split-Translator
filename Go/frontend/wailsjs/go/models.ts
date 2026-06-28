export namespace main {
	
	export class GambarResponse {
	    status: boolean;
	    gambar_base64: string;
	
	    static createFrom(source: any = {}) {
	        return new GambarResponse(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.status = source["status"];
	        this.gambar_base64 = source["gambar_base64"];
	    }
	}
	export class LanguagesResponse {
	    status: boolean;
	    languages: Record<string, string>;
	
	    static createFrom(source: any = {}) {
	        return new LanguagesResponse(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.status = source["status"];
	        this.languages = source["languages"];
	    }
	}
	export class TerjemahanResponse {
	    status: boolean;
	    terjemahan: string;
	    isLokal: boolean;
	    message?: string;
	
	    static createFrom(source: any = {}) {
	        return new TerjemahanResponse(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.status = source["status"];
	        this.terjemahan = source["terjemahan"];
	        this.isLokal = source["isLokal"];
	        this.message = source["message"];
	    }
	}
	export class UploadResponse {
	    status: boolean;
	    message: string;
	    total_halaman: number;
	
	    static createFrom(source: any = {}) {
	        return new UploadResponse(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.status = source["status"];
	        this.message = source["message"];
	        this.total_halaman = source["total_halaman"];
	    }
	}

}

