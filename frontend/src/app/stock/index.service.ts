import { Injectable } from '@angular/core';
import { Http, Response, URLSearchParams } from '@angular/http';

import 'rxjs/add/operator/map';

@Injectable()
export class IndexService {

  constructor(private http: Http) { }

  getIndices(page: number, size: number, sortField?: string, sortOrder?: number) {
    let url = "http://localhost:8080/indices";
    let params = new URLSearchParams();
    params.set("page", page.toString());
    params.set("size", size.toString());
    if (sortField && sortOrder)
      if(sortOrder == 1)
        params.set("sort", sortField + ",asc");
      else
        params.set("sort", sortField + ",desc");
    return this.http.get(url, {search: params})
      .map(this.extractData);
  }

  getIndexById(id: number) {
    let url = "http://localhost:8080/indices/" + id;

    return this.http.get(url)
      .map(this.extractData);
  }

  getIndexByLink(link: string) {
    return this.http.get(link)
      .map(this.extractData);
  }

  extractData(resp: Response) {
    return resp.json();
  }

}