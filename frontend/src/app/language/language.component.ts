import { Component, OnInit, LOCALE_ID, Inject } from '@angular/core';

import { SelectItem } from 'primeng/primeng';

import { environment } from '../../environments/environment';

@Component({
  selector: 'app-language',
  templateUrl: './language.component.html',
  styleUrls: ['./language.component.css']
})
export class LanguageComponent implements OnInit {
  languages: SelectItem[] = [];
  selectedLanguage: string = 'en';
  constructor(@Inject(LOCALE_ID) private locale: string) { }

  ngOnInit() {
    this.languages = [
      {label: 'Deutsch', value: 'de'},
      {label: 'English', value: 'en'}
    ];
    
    if (this.locale && this.locale.length >= 2)
        this.setLanguage(this.locale.substring(0, 2));
  }
  
  setLanguage(language: any, doRouting: boolean = false) {
    debugger
    if (doRouting)
      window.location.href = environment.baseUrl + '/' + language.value;
    else
      this.selectedLanguage = language;
  }

}
