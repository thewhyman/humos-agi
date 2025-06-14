import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatSidenav } from '@angular/material/sidenav';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { map, shareReplay } from 'rxjs/operators';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatSidenavModule,
    MatListModule
  ],
  templateUrl: './app.component.html'
})
export class AppComponent implements OnInit, OnDestroy {
  @ViewChild('sidenav', { static: true }) sidenav!: MatSidenav;
  title = 'HumOS AI';
  isHandset$: Observable<boolean>;
  private destroy$ = new Subject<void>();

  navItems = [
    { path: '/face-detection', icon: 'face_retouching_natural', label: 'Face Detection' },
    { path: '/voice-analysis', icon: 'record_voice_over', label: 'Voice Analysis' },
  ];

  constructor(private breakpointObserver: BreakpointObserver) {
    this.isHandset$ = this.breakpointObserver.observe([
      Breakpoints.Handset,
      Breakpoints.TabletPortrait,
    ]).pipe(
      map(result => result.matches),
      shareReplay()
    );
  }

  toggleTheme(): void {
    // TODO: Implement theme toggling logic
    document.body.classList.toggle('dark-theme');
  }

  handleNavClick(event: Event): void {
    // Close the sidenav on mobile after navigation
    const isHandset = this.breakpointObserver.isMatched([
      Breakpoints.Handset,
      Breakpoints.TabletPortrait
    ]);
    
    if (isHandset && this.sidenav) {
      this.sidenav.close();
    }
  }

  toggleSidenav(): void {
    if (this.sidenav) {
      this.sidenav.toggle();
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  ngOnInit(): void {
    // Check if the app is running as a PWA
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('Running as PWA');
    }
  }
}
