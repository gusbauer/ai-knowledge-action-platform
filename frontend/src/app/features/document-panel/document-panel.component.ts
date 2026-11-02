import { Component, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ApiService } from '../../core/services/api.service';
import { DocumentItem } from '../../core/models/api.models';

@Component({
  selector: 'app-document-panel',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './document-panel.component.html',
  styleUrl: './document-panel.component.scss',
})
export class DocumentPanelComponent implements OnInit {
  readonly documents = signal<DocumentItem[]>([]);
  readonly loading = signal(false);
  readonly uploading = signal(false);
  readonly error = signal<string | null>(null);

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.error.set(null);

    this.api.listDocuments().subscribe({
      next: (documents) => {
        this.documents.set(documents);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load documents.');
        this.loading.set(false);
      },
    });
  }

  selectFile(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input?.files?.[0];

    if (!file) {
      return;
    }

    this.uploading.set(true);
    this.error.set(null);

    this.api.uploadDocument(file).subscribe({
      next: () => {
        this.uploading.set(false);
        if (input) {
          input.value = '';
        }
        this.refresh();
      },
      error: () => {
        this.uploading.set(false);
        this.error.set('Upload failed.');
      },
    });
  }

  formatSize(bytes: number): string {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }
}
