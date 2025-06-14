import { Injectable, OnDestroy } from '@angular/core';
import * as faceapi from 'face-api.js';
import { FaceDetectionResult } from '../models/face-detection.model';

@Injectable({
  providedIn: 'root'
})
export class FaceDetectionService implements OnDestroy {
  private isModelLoaded = false;
  private videoElement: HTMLVideoElement | null = null;
  private canvasElement: HTMLCanvasElement | null = null;
  private stream: MediaStream | null = null;
  private detectionInterval: any = null;

  constructor() {}

  async initialize(videoElement: HTMLVideoElement, canvasElement: HTMLCanvasElement): Promise<void> {
    this.videoElement = videoElement;
    this.canvasElement = canvasElement;
    
    try {
      // Load models
      await faceapi.nets.tinyFaceDetector.loadFromUri('/assets/models');
      await faceapi.nets.faceLandmark68Net.loadFromUri('/assets/models');
      await faceapi.nets.faceRecognitionNet.loadFromUri('/assets/models');
      await faceapi.nets.faceExpressionNet.loadFromUri('/assets/models');
      await faceapi.nets.ageGenderNet.loadFromUri('/assets/models');
      
      this.isModelLoaded = true;
      console.log('Face detection models loaded');
    } catch (error) {
      console.error('Error loading face detection models:', error);
      throw error;
    }
  }

  async startDetection(callback: (result: FaceDetectionResult | null) => void): Promise<void> {
    if (!this.isModelLoaded || !this.videoElement || !this.canvasElement) {
      throw new Error('Face detection not initialized');
    }

    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      
      this.videoElement.srcObject = this.stream;
      await this.videoElement.play();
      
      // Set canvas dimensions to match video
      this.canvasElement.width = this.videoElement.videoWidth;
      this.canvasElement.height = this.videoElement.videoHeight;
      
      // Start detection loop
      this.detectionInterval = setInterval(async () => {
        const detections = await faceapi
          .detectAllFaces(this.videoElement!, new faceapi.TinyFaceDetectorOptions())
          .withFaceLandmarks()
          .withFaceExpressions()
          .withAgeAndGender();
        
        if (detections.length > 0) {
          const detection = detections[0]; // Get the first face
          const result: FaceDetectionResult = {
            expressions: detection.expressions as any,
            age: Math.round(detection.age),
            gender: detection.gender,
            genderProbability: detection.genderProbability,
            box: {
              x: detection.detection.box.x,
              y: detection.detection.box.y,
              width: detection.detection.box.width,
              height: detection.detection.box.height
            }
          };
          
          callback(result);
          this.drawDetectionBox(result);
        } else {
          callback(null);
        }
      }, 100); // Run detection every 100ms
      
    } catch (error) {
      console.error('Error starting face detection:', error);
      throw error;
    }
  }

  stopDetection(): void {
    if (this.detectionInterval) {
      clearInterval(this.detectionInterval);
      this.detectionInterval = null;
    }
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    
    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }
  }

  private drawDetectionBox(result: FaceDetectionResult): void {
    if (!this.canvasElement || !this.videoElement) return;
    
    const ctx = this.canvasElement.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
    
    // Draw video frame
    ctx.drawImage(
      this.videoElement,
      0, 0, this.videoElement.videoWidth, this.videoElement.videoHeight,
      0, 0, this.canvasElement.width, this.canvasElement.height
    );
    
    // Draw face box
    const { x, y, width, height } = result.box;
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, width, height);
    
    // Draw text
    ctx.fillStyle = '#00ff00';
    ctx.font = '16px Arial';
    ctx.fillText(`Age: ${result.age}`, x, y - 10);
    ctx.fillText(`Gender: ${result.gender} (${Math.round((result.genderProbability || 0) * 100)}%)`, x, y - 30);
    
    // Draw expressions
    let yOffset = y + height + 20;
    Object.entries(result.expressions).forEach(([emotion, value]) => {
      ctx.fillText(`${emotion}: ${(value * 100).toFixed(1)}%`, x, yOffset);
      yOffset += 20;
    });
  }

  ngOnDestroy(): void {
    this.stopDetection();
  }
}
