import { Component, ViewChild, ElementRef, AfterViewInit, OnDestroy } from '@angular/core';
import * as faceapi from 'face-api.js';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

type EmotionType = 'neutral' | 'happy' | 'sad' | 'angry' | 'fearful' | 'disgusted' | 'surprised';

interface DetectionResult {
  expressions: {
    neutral: number;
    happy: number;
    sad: number;
    angry: number;
    fearful: number;
    disgusted: number;
    surprised: number;
    [key: string]: number;
  } | null;
  age?: number;
  gender?: string;
  genderProbability?: number;
}

@Component({
  selector: 'app-face-detection',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './face-detection.component.html',
  styleUrls: ['./face-detection.component.scss']
})
export class FaceDetectionComponent implements AfterViewInit, OnDestroy {
  private detectionInterval: any;
  private modelsLoaded = false;
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvasElement') canvasElement!: ElementRef<HTMLCanvasElement>;
  
  private video!: HTMLVideoElement;
  private canvas!: HTMLCanvasElement;
  private canvasCtx: CanvasRenderingContext2D | null = null;
  
  isDetecting = false;
  detectionResult: DetectionResult | null = null;
  error: string | null = null;

  async ngAfterViewInit() {
    this.video = this.videoElement.nativeElement;
    this.canvas = this.canvasElement.nativeElement;
    this.canvasCtx = this.canvas.getContext('2d');
    
    try {
      // Load face-api.js models
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/assets/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/assets/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/assets/models'),
        faceapi.nets.faceExpressionNet.loadFromUri('/assets/models'),
        faceapi.nets.ageGenderNet.loadFromUri('/assets/models')
      ]);
      this.modelsLoaded = true;
      this.startVideo();
    } catch (err) {
      console.error('Error loading models:', err);
      this.error = 'Failed to load face detection models. Please try again later.';
    }
  }

  ngOnDestroy() {
    this.stopDetection();
    if (this.video.srcObject) {
      const tracks = (this.video.srcObject as MediaStream).getTracks();
      tracks.forEach(track => track.stop());
    }
  }

  private async startVideo() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      this.video.srcObject = stream;
      this.video.play();
      this.startDetection();
    } catch (err) {
      console.error('Error accessing camera:', err);
      this.error = 'Could not access camera. Please ensure you have granted camera permissions.';
    }
  }

  private async startDetection() {
    this.isDetecting = true;
    this.detectionInterval = setInterval(async () => {
      if (!this.modelsLoaded || !this.video.readyState) return;
      
      // Set canvas dimensions to match video
      this.canvas.width = this.video.videoWidth;
      this.canvas.height = this.video.videoHeight;
      
      try {
        // Detect faces
        const detections = await faceapi.detectAllFaces(
          this.video,
          new faceapi.TinyFaceDetectorOptions()
        ).withFaceLandmarks().withFaceExpressions().withAgeAndGender();
        
        // Clear canvas
        this.canvasCtx?.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (detections.length > 0) {
          // Get the first face
          const detection = detections[0];
          
          if (detection.expressions) {
            // Convert FaceExpressions to our format
            const expressions = {
              neutral: detection.expressions.neutral || 0,
              happy: detection.expressions.happy || 0,
              sad: detection.expressions.sad || 0,
              angry: detection.expressions.angry || 0,
              fearful: detection.expressions.fearful || 0,
              disgusted: detection.expressions.disgusted || 0,
              surprised: detection.expressions.surprised || 0
            };
            
            // Update detection result
            this.detectionResult = {
              expressions,
              age: Math.round(detection.age || 0),
              gender: detection.gender,
              genderProbability: detection.genderProbability
            };
            
            // Draw detection box
            const box = detection.detection.box;
            this.canvasCtx!.strokeStyle = '#00ff00';
            this.canvasCtx!.lineWidth = 2;
            this.canvasCtx!.strokeRect(box.x, box.y, box.width, box.height);
          }
        } else {
          this.detectionResult = null;
        }
      } catch (err) {
        console.error('Error during face detection:', err);
        this.detectionResult = null;
      }
    }, 100);
  }

  stopDetection(): void {
    if (this.detectionInterval) {
      clearInterval(this.detectionInterval);
      this.detectionInterval = null;
    }
    this.isDetecting = false;
    this.detectionResult = null;
    
    // Stop all video tracks
    if (this.video.srcObject) {
      const stream = this.video.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      this.video.srcObject = null;
    }
  }

  getEmotionEmoji(expressions: DetectionResult['expressions']): string {
    if (!expressions) return '❓';
    
    const emotion = Object.entries(expressions).reduce((a, b) => 
      (a[1] > b[1] ? a : b)
    ) as [EmotionType, number];
    
    const emojiMap: Record<EmotionType, string> = {
      neutral: '😐',
      happy: '😊',
      sad: '😢',
      angry: '😠',
      fearful: '😨',
      disgusted: '🤢',
      surprised: '😲'
    };
    
    return emojiMap[emotion[0]] || '❓';
  }

  getDominantEmotion(expressions: DetectionResult['expressions']): string {
    if (!expressions) return 'Unknown';
    
    return Object.entries(expressions).reduce((a, b) => 
      (a[1] > b[1] ? a : b)
    )[0];
  }
  
  getEmotionPercentage(expressions: DetectionResult['expressions'], emotion: string): number {
    if (!expressions) return 0;
    
    const total = Object.values(expressions).reduce((sum, val) => sum + val, 0);
    return total > 0 ? (expressions[emotion] / total) * 100 : 0;
  }

  async toggleDetection(): Promise<void> {
    if (this.isDetecting) {
      this.stopDetection();
    } else {
      try {
        this.isDetecting = true;
        this.error = null;
        
        // Start the video and detection if not already started
        if (!this.video.srcObject) {
          await this.startVideo();
        } else if (!this.detectionInterval) {
          this.startDetection();
        }
      } catch (err: unknown) {
        console.error('Error during face detection:', err);
        this.error = 'Failed to start face detection. Please ensure camera access is allowed.';
        this.isDetecting = false;
      }
    }
  }

}
