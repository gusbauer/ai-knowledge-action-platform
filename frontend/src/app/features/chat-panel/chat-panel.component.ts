import { Component, signal } from '@angular/core';

import { FormsModule } from '@angular/forms';

import { CommonModule } from '@angular/common';

import { AgentResponse, AgentSource } from '../../core/models/api.models';

import { ApiService } from '../../core/services/api.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: AgentSource[];
}

@Component({
  selector: 'app-chat-panel',

  standalone: true,

  imports: [CommonModule, FormsModule],

  templateUrl: './chat-panel.component.html',

  styleUrl: './chat-panel.component.scss',
})
export class ChatPanelComponent {
  question = '';

  readonly messages = signal<ChatMessage[]>([]);

  readonly loading = signal(false);

  readonly pendingApproval = signal<AgentResponse | null>(null);

  readonly threadId = signal<string | null>(localStorage.getItem('agent_thread_id'));

  constructor(private readonly api: ApiService) {}

  send(): void {
    const question = this.question.trim();

    if (!question || this.loading()) {
      return;
    }

    this.messages.update((messages) => [
      ...messages,
      {
        role: 'user',
        content: question,
      },
    ]);

    this.question = '';

    this.loading.set(true);

    this.api
      .askAgent({
        question,
        thread_id: this.threadId() ?? undefined,
      })
      .subscribe({
        next: (response) => {
          this.processResponse(response);

          this.loading.set(false);
        },

        error: (error) => {
          console.error(error);

          this.messages.update((messages) => [
            ...messages,
            {
              role: 'assistant',
              content: 'No se pudo completar la solicitud.',
            },
          ]);

          this.loading.set(false);
        },
      });
  }

  approve(): void {
    this.resume(true);
  }

  reject(): void {
    this.resume(false);
  }

  newConversation(): void {
    localStorage.removeItem('agent_thread_id');

    this.threadId.set(null);

    this.messages.set([]);

    this.pendingApproval.set(null);
  }

  private resume(approved: boolean): void {
    const threadId = this.threadId();

    if (!threadId) {
      return;
    }

    this.loading.set(true);

    this.api
      .resumeAgent({
        thread_id: threadId,
        approved,
      })
      .subscribe({
        next: (response) => {
          this.pendingApproval.set(null);

          this.processResponse(response);

          this.loading.set(false);
        },

        error: (error) => {
          console.error(error);

          this.loading.set(false);
        },
      });
  }

  private processResponse(response: AgentResponse): void {
    this.threadId.set(response.thread_id);

    localStorage.setItem('agent_thread_id', response.thread_id);

    if (response.status === 'interrupted') {
      this.pendingApproval.set(response);

      return;
    }

    this.pendingApproval.set(null);

    if (response.answer) {
      this.messages.update((messages) => [
        ...messages,
        {
          role: 'assistant',
          content: response.answer!,
          sources: response.sources,
        },
      ]);
    }
  }
}
