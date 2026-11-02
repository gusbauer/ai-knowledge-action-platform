import { Component } from '@angular/core';

import { ChatPanelComponent } from './features/chat-panel/chat-panel.component';
import { DocumentPanelComponent } from './features/document-panel/document-panel.component';
import { SystemStatusComponent } from './features/system-status/system-status.component';

@Component({
  selector: 'app-root',

  standalone: true,

  imports: [ChatPanelComponent, DocumentPanelComponent, SystemStatusComponent],

  templateUrl: './app.component.html',

  styleUrl: './app.component.scss',
})
export class AppComponent {}
