#!/bin/bash

# Build and Push Docker Image

echo "Building Docker image..."
docker build --platform linux/amd64 -t gcr.io/jagwirerobotic/cloudrun-firestore .

echo "Authenticating Docker with Google Cloud..."
gcloud auth configure-docker

echo "Pushing Docker image to Google Container Registry..."
docker push gcr.io/jagwirerobotic/cloudrun-firestore

# Deploy Cloud Run service

echo "Deploying Cloud Run service..."
gcloud run deploy jag-wirer-robotic-service-abby \
    --image=gcr.io/jagwirerobotic/cloudrun-firestore \
    --region=us-central1 \
    --allow-unauthenticated \
    --service-account=svc-tf-ja-wire-robotics@jagwirerobotic.iam.gserviceaccount.com

echo "Deployment completed successfully!"
