import { Routes } from '@angular/router';
import { FaceDetectionComponent } from './components/face-detection/face-detection.component';
import { VoiceAnalysisComponent } from './components/voice-analysis/voice-analysis.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'face-detection',
    pathMatch: 'full'
  },
  {
    path: 'face-detection',
    component: FaceDetectionComponent,
    title: 'Face Detection | HumOS AI'
  },
  {
    path: 'voice-analysis',
    component: VoiceAnalysisComponent,
    title: 'Voice Analysis | HumOS AI'
  },
  {
    path: '**',
    redirectTo: 'face-detection'
  }
];
