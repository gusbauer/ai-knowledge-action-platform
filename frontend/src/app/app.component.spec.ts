import { TestBed } from '@angular/core/testing';

import { AppComponent } from './app.component';
import as from '@angular/common/locales/extra/as';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);

    const app = fixture.componentInstance;

    expect(app).toBeTruthy();
  });

  it('should render the main title', async () => {
    const fixture = TestBed.createComponent(AppComponent);

    await fixture.whenStable();

    const compiled: HTMLElement = fixture.nativeElement;

    expect(compiled.querySelector('h1')?.textContent).toContain('Knowledge & Action');
  });
});
