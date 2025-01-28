#!/bin/bash

# Deploy Cloud Run service

gcloud run deploy jag-wirer-robotic-service \
    --image=gcr.io/jagwirerobotic/cloudrun-firestore \
    --region=us-central1 \
    --allow-unauthenticated \
    --service-account=svc-tf-ja-wire-robotics@jagwirerobotic.iam.gserviceaccount.com
