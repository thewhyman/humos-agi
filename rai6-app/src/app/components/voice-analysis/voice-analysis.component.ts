import { Component, OnDestroy, OnInit, ViewChild, ElementRef, AfterViewInit, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { VoiceAnalysisService, VoiceAnalysisResult } from '../../services/voice-analysis.service';
import { Subscription } from 'rxjs';

// Declare webkitAudioContext for TypeScript
declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
  }
}

@Component({
  selector: 'app-voice-analysis',
  standalone: true,
  imports: [
    CommonModule, 
    MatCardModule, 
    MatButtonModule, 
    MatIconModule,
    MatProgressBarModule
  ],
  templateUrl: './voice-analysis.component.html',
  styleUrls: ['./voice-analysis.component.scss']
})
export class VoiceAnalysisComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('visualizer') private visualizerRef!: ElementRef<HTMLCanvasElement>;
  
  isListening = false;
  emotions: ('happy' | 'sad' | 'angry' | 'fearful' | 'neutral')[] = ['happy', 'sad', 'angry', 'fearful', 'neutral'];
  analysisResult: VoiceAnalysisResult = {
    text: '',
    mood: 'neutral',
    confidence: 0,
    emotions: {
      happy: 0,
      sad: 0,
      angry: 0,
      fearful: 0,
      neutral: 1
    },
    tone: {
      pitch: 0.5,
      rate: 1.0,
      volume: 0.5
    }
  };
  error: string | null = null;
  private analysisSubscription: Subscription | null = null;
  
  // Visualizer properties
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private dataArray: Uint8Array | null = null;
  private animationFrameId: number | null = null;
  private canvasCtx: CanvasRenderingContext2D | null = null;
  
  constructor(
    private voiceAnalysisService: VoiceAnalysisService,
    private ngZone: NgZone
  ) {}
  
  ngOnInit(): void {
    // Initialization logic if needed
  }
  
  ngAfterViewInit(): void {
    this.initializeVisualizer();
  }
  
  ngOnDestroy(): void {
    this.stopListening();
    this.cleanupVisualizer();
  }
  
  toggleListening(): void {
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }
  
  private startListening(): void {
    this.isListening = true;
    this.error = null;
    
    this.analysisSubscription = this.voiceAnalysisService.startListening().subscribe({
      next: (result) => {
        this.analysisResult = result;
      },
      error: (error) => {
        console.error('Error in voice analysis:', error);
        this.error = 'Error analyzing voice. Please check microphone permissions.';
        this.isListening = false;
      }
    });
    
    this.startVisualizer();
  }
  
  private stopListening(): void {
    try {
      this.voiceAnalysisService.stopListening();
      
      if (this.analysisSubscription) {
        this.analysisSubscription.unsubscribe();
        this.analysisSubscription = null;
      }
      
      this.isListening = false;
      this.stopVisualizer();
    } catch (error) {
      console.error('Error stopping listening:', error);
      this.error = 'Error stopping voice analysis. Please try again.';
    }
  }
  
  private initializeVisualizer(): void {
    if (this.visualizerRef?.nativeElement) {
      const canvas = this.visualizerRef.nativeElement;
      canvas.width = canvas.offsetWidth;
      canvas.height = 100;
      // No need to store canvasCtx as we'll get it fresh in visualize()
    }
  }
  
  private startVisualizer(): void {
    try {
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      
      navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        .then((stream) => {
          if (!this.audioContext) {
            throw new Error('Audio context not initialized');
          }
          
          const source = this.audioContext.createMediaStreamSource(stream);
          this.analyser = this.audioContext.createAnalyser();
          source.connect(this.analyser);
          this.analyser.fftSize = 256;
          
          const bufferLength = this.analyser.frequencyBinCount;
          this.dataArray = new Uint8Array(bufferLength);
          
          this.visualize();
        })
        .catch((error: Error) => {
          console.error('Error accessing microphone:', error);
          this.error = 'Could not access microphone. Please check permissions.';
        });
    } catch (error) {
      console.error('Error initializing audio context:', error);
      this.error = 'Error initializing audio. Please try again.';
    }
  }
  
  private visualize(): void {
    if (!this.analyser || !this.dataArray || !this.visualizerRef || !this.visualizerRef.nativeElement) {
      return;
    }
    
    const canvas = this.visualizerRef.nativeElement;
    const canvasCtx = canvas.getContext('2d');
    
    if (!canvasCtx) {
      console.error('Could not get 2D context for canvas');
      return;
    }
    
    const WIDTH = canvas.width;
    const HEIGHT = canvas.height;
    
    const draw = (): void => {
      if (!this.analyser || !this.dataArray) {
        return;
      }
      
      // Store animation frame ID before the async operation
      const animationId = requestAnimationFrame(() => this.ngZone.run(draw));
      this.animationFrameId = animationId;
      
      try {
        this.analyser.getByteFrequencyData(this.dataArray);
        
        // Clear the canvas
        canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
        
        // Draw background
        canvasCtx.fillStyle = 'rgb(0, 0, 0)';
        canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
        
        const barWidth = Math.max(1, (WIDTH / this.dataArray.length) * 2.5);
        let x = 0;
        
        for (let i = 0; i < this.dataArray.length; i++) {
          const barHeight = (this.dataArray[i] / 255) * HEIGHT;
          
          // Skip very small bars to improve performance
          if (barHeight < 1) {
            x += barWidth + 1;
            continue;
          }
          
          // Create gradient for the bar
          const gradient = canvasCtx.createLinearGradient(0, HEIGHT - barHeight, 0, HEIGHT);
          
          // Set gradient colors based on mood
          const { mood } = this.analysisResult;
          switch (mood) {
            case 'happy':
              gradient.addColorStop(0, '#4caf50');
              gradient.addColorStop(1, '#8bc34a');
              break;
            case 'sad':
              gradient.addColorStop(0, '#2196f3');
              gradient.addColorStop(1, '#64b5f6');
              break;
            case 'angry':
              gradient.addColorStop(0, '#f44336');
              gradient.addColorStop(1, '#ff7043');
              break;
            case 'fearful':
              gradient.addColorStop(0, '#9c27b0');
              gradient.addColorStop(1, '#ce93d8');
              break;
            default:
              gradient.addColorStop(0, '#9e9e9e');
              gradient.addColorStop(1, '#bdbdbd');
          }
          
          // Draw the bar
          canvasCtx.fillStyle = gradient;
          canvasCtx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);
          
          x += barWidth + 1;
        }
      } catch (error) {
        console.error('Error in visualization:', error);
        // Stop the animation if there's an error
        if (this.animationFrameId === animationId) {
          this.animationFrameId = null;
        }
        return;
      }
    };
    
    // Start the animation loop
    this.ngZone.runOutsideAngular(() => {
      draw();
    });
  }
  
  private stopVisualizer(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    
    if (this.audioContext) {
      if (this.audioContext.state !== 'closed') {
        this.audioContext.close().catch(error => {
          console.error('Error closing audio context:', error);
        });
      }
      this.audioContext = null;
    }
    
    this.analyser = null;
    this.dataArray = null;
  }
  
  private cleanupVisualizer(): void {
    this.stopVisualizer();
    // No need to set canvasCtx to null as it's recreated on each visualization
  }
  
  getMoodEmoji(mood: string): string {
    switch (mood) {
      case 'happy': return '😊';
      case 'sad': return '😢';
      case 'angry': return '😠';
      case 'fearful': return '😨';
      default: return '😐';
    }
  }
  
  getConfidenceColor(confidence: number): string {
    if (confidence > 0.7) return 'primary';
    if (confidence > 0.4) return 'accent';
    return 'warn';
  }
}
