# Deployment Guide - Render

This guide explains how to deploy Skinny Legend to Render with both frontend and backend.

## Prerequisites

- GitHub repository (already set up at https://github.com/Ben-Davis1/skinny-legend)
- Render account (sign up at https://render.com)
- Anthropic API key

## Deployment Steps

### 1. Connect to Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub account if not already connected
4. Select the `skinny-legend` repository

### 2. Configure Services

Render will automatically detect the `render.yaml` file and create two services:

- **skinny-legend-api** (Backend) - Python web service
- **skinny-legend** (Frontend) - Node web service

### 3. Set Environment Variables

#### Backend (skinny-legend-api)

Set these in the Render dashboard:

- `ANTHROPIC_API_KEY`: Your Anthropic API key (get from https://console.anthropic.com)
- `ALLOWED_ORIGINS`: https://skinny-legend.onrender.com (auto-configured in render.yaml)

### 4. Deploy

Click "Apply" to deploy both services. The deployment will:

1. Install dependencies
2. Build the frontend
3. Initialize the database
4. Start both services

### 5. Access Your App

After deployment (takes ~5-10 minutes):

- **Frontend**: https://skinny-legend.onrender.com
- **Backend API**: https://skinny-legend-api.onrender.com

## URLs

The services will be available at:

- Frontend: `https://skinny-legend.onrender.com`
- Backend: `https://skinny-legend-api.onrender.com`
- Health Check: `https://skinny-legend-api.onrender.com/health`

## Important Notes

### Free Tier Limitations

Render's free tier:
- Spins down after 15 minutes of inactivity
- Cold start takes 30-60 seconds
- Database is stored on disk (persists between deployments)
- 750 hours/month free (enough for 1 service 24/7)

### Database Persistence

The SQLite database is stored at `/opt/render/project/src/backend/skinny_legend.db` and persists between deployments.

### File Uploads

Images are stored at `/opt/render/project/src/backend/uploads` and persist between deployments.

## Updating CORS

If you deploy the frontend to a different URL, update the `ALLOWED_ORIGINS` environment variable in the backend service:

1. Go to Render Dashboard → skinny-legend-api
2. Environment → Edit
3. Update `ALLOWED_ORIGINS` to include your frontend URL
4. Save changes (auto-redeploys)

## Troubleshooting

### Check Logs

- Go to Render Dashboard
- Click on the service
- View logs in the "Logs" tab

### Cold Start Issues

Free tier services sleep after inactivity. First request may take 30-60 seconds.

### Database Issues

If database initialization fails:
1. Check logs for errors
2. May need to manually run: `python3 -c "from database import init_db; init_db()"`

### CORS Errors

If you get CORS errors:
1. Check backend logs
2. Verify `ALLOWED_ORIGINS` includes your frontend URL
3. Make sure frontend is using correct API URL

## Manual Deployment (Alternative)

If you prefer to deploy manually without render.yaml:

### Backend

1. New + → Web Service
2. Connect repository
3. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `bash start.sh`
   - Add environment variables

### Frontend

1. New + → Static Site
2. Connect repository
3. Settings:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Add environment variables

## Updating After Changes

Render auto-deploys when you push to `main` branch:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Both services will automatically redeploy.

## Custom Domain (Optional)

To use a custom domain:
1. Go to service settings
2. Add custom domain
3. Follow DNS configuration instructions
4. Update ALLOWED_ORIGINS if using custom domain for frontend
