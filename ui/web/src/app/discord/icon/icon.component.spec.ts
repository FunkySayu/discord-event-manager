import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {DiscordModule} from '../discord.module';
import {IconComponent} from './icon.component';

describe('IconComponent', () => {
  let component: IconComponent;
  let fixture: ComponentFixture<IconComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [DiscordModule],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('displays nothing if no inputs are passed', () => {
    const img = fixture.nativeElement.querySelector('img');
    expect(img).toBeNull();
  });

  it('displays an image relative to the Discord CDN', () => {
    component.type = 'avatars';
    component.id = '123';
    component.icon = '456';
    fixture.detectChanges();

    const img = fixture.nativeElement.querySelector('img');
    expect(img).not.toBeNull();
    expect(img.getAttribute('src')).toBe('https://cdn.discordapp.com/avatars/123/456.png');
  });
});
