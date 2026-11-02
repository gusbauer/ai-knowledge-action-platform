import { Component, OnInit, signal } from '@angular/core';

import { ApiService } from '../../core/services/api.service';

import { HealthReadyResponse } from '../../core/models/api.models';

@Component({
  selector: 'app-system-status',

  standalone: true,

  templateUrl: './system-status.component.html',

  styleUrl: './system-status.component.scss',
})
export class SystemStatusComponent implements OnInit {
  readonly health = signal<HealthReadyResponse | null>(null);

  readonly online = signal(false);

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.api.getReadiness().subscribe({
      next: (health) => {
        this.health.set(health);

        this.online.set(health.status === 'ready');
      },

      error: () => {
        this.health.set(null);
        this.online.set(false);
      },
    });
  }
}
