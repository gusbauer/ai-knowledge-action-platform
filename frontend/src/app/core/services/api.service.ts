import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';

import {
  AgentRequest,
  AgentResponse,
  AgentResumeRequest,
  HealthReadyResponse,
} from '../models/api.models';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly baseUrl = 'http://127.0.0.1:8000';

  constructor(private readonly http: HttpClient) {}

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
