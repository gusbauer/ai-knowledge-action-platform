import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  AgentRequest,
  AgentResponse,
  AgentResumeRequest,
  HealthReadyResponse,
  DocumentItem,
} from '../models/api.models';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly baseUrl = environment.apiBaseUrl;

  constructor(private readonly http: HttpClient) {}

  listDocuments(): Observable<DocumentItem[]> {
    return this.http.get<DocumentItem[]>(`${this.baseUrl}/documents`);
  }

  uploadDocument(file: File): Observable<DocumentItem> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<DocumentItem>(`${this.baseUrl}/documents/upload`, formData);
  }

  askAgent(request: AgentRequest): Observable<AgentResponse> {
    return this.http.post<AgentResponse>(`${this.baseUrl}/agent/ask`, request);
  }

  resumeAgent(request: AgentResumeRequest): Observable<AgentResponse> {
    return this.http.post<AgentResponse>(`${this.baseUrl}/agent/resume`, request);
  }

  getReadiness(): Observable<HealthReadyResponse> {
    return this.http.get<HealthReadyResponse>(`${this.baseUrl}/health/ready`);
  }
}
