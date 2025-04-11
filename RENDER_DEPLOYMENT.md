# Deploying to Render

This guide will help you deploy the waste classification application to Render.

## Prerequisites

1. A GitHub account
2. A Render account (sign up at [render.com](https://render.com))
3. Git LFS installed locally

## Step 1: Set up Git LFS

```bash
# Install Git LFS
brew install git-lfs  # For macOS

# Initialize Git LFS
git lfs install

# Track model files
git lfs track "*.keras"
git lfs track "*.h5"

# Add .gitattributes
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

## Step 2: Push to GitHub

```bash
# Add all files
git add .

# Commit changes
git commit -m "Prepare for deployment"

# Push to GitHub
git push origin main
```

## Step 3: Deploy to Render

1. Log in to your Render account
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - Name: `waste-classification-app` (or your preferred name)
   - Environment: `Python`
   - Build Command: Leave as is (will use render.yaml)
   - Start Command: Leave as is (will use render.yaml)
   - Select the branch you want to deploy (usually `main`)

5. Click "Create Web Service"

## Step 4: Monitor Deployment

1. Watch the build logs in the Render dashboard
2. Once deployed, you'll get a URL for your application
3. Test the application by visiting the URL
4. Check the model status at `/model-status` endpoint

## Troubleshooting

### Model Loading Issues

If the model fails to load:

1. Check the Render logs for errors
2. Verify the model URL is correct
3. Try manually downloading the model to test the URL
4. Consider hosting the model on a different service (like AWS S3)

### Deployment Issues

If deployment fails:

1. Check the build logs for errors
2. Verify all dependencies are in requirements.txt
3. Make sure Git LFS is properly set up
4. Check if the model file is being tracked by Git LFS

## Updating the Application

To update your application:

1. Make changes to your code
2. Commit and push to GitHub
3. Render will automatically redeploy

```bash
git add .
git commit -m "Update application"
git push origin main
``` 