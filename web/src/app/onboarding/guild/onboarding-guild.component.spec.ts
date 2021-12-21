import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OnboardingGuildComponent } from './onboarding-guild.component';

describe('GuildComponent', () => {
  let component: OnboardingGuildComponent;
  let fixture: ComponentFixture<OnboardingGuildComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OnboardingGuildComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OnboardingGuildComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
