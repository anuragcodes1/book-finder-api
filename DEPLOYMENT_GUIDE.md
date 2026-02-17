# Railway Deployment Guide

## Prerequisites Setup

### 1. Install Xcode Command Line Tools (Required for Git)

```bash
xcode-select --install
```

Click "Install" in the popup. Wait for installation to complete (5-10 minutes).

Verify installation:
```bash
git --version
```

### 2. Install Python (if not already installed)

Check if Python is installed:
```bash
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/) or use Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```

## Local Testing (Optional but Recommended)

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app locally

```bash
python app.py
```

Visit: http://localhost:5000

Test the API:
```bash
curl "http://localhost:5000/api/books?author=Isaac%20Asimov"
```

## Deploy to Railway (via GitHub)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `book-finder-api`
3. Keep it Public or Private (your choice)
4. Don't initialize with README
5. Click "Create repository"

### Step 2: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Book Finder API"

# Set main branch
git branch -M main

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/book-finder-api.git

# Push to GitHub
git push -u origin main
```

If prompted for credentials:
- Username: your GitHub username
- Password: use a Personal Access Token (not your password)
  - Generate token at: https://github.com/settings/tokens
  - Select "repo" scope
  - Copy and paste the token as password

### Step 3: Deploy on Railway

1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway
4. Click "New Project"
5. Select "Deploy from GitHub repo"
6. Choose `book-finder-api` from the list
7. Click "Deploy Now"

Railway will automatically:
- Detect it's a Python app
- Install dependencies from requirements.txt
- Run the app using the Procfile
- Assign a public URL

### Step 4: Configure Domain

1. Click on your deployed project
2. Go to "Settings" tab
3. Scroll to "Networking" section
4. Click "Generate Domain"
5. Your API is now live at: `https://your-app-name.up.railway.app`

### Step 5: Test Your Live API

```bash
# Replace YOUR_DOMAIN with your Railway domain
curl "https://your-app-name.up.railway.app/api/books?author=Isaac%20Asimov"
```

Or visit in browser:
```
https://your-app-name.up.railway.app/
```

## API Endpoints

Once deployed, your API will have these endpoints:

- `GET /` - API documentation
- `GET /health` - Health check
- `GET /api/books?author=<name>` - Search books by author

## Example Usage

```bash
# Get API info
curl https://your-app-name.up.railway.app/

# Health check
curl https://your-app-name.up.railway.app/health

# Search for books
curl "https://your-app-name.up.railway.app/api/books?author=J.K.%20Rowling"
```

## Troubleshooting

### Build Fails on Railway

Check the build logs in Railway dashboard. Common issues:
- Missing dependencies: Add to requirements.txt
- Python version: Specified in runtime.txt (currently 3.11.7)

### API Returns 500 Error

Check the deployment logs in Railway:
1. Click on your project
2. Go to "Deployments" tab
3. Click on the latest deployment
4. View logs for error messages

### Need to Update Code

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push

# Railway will automatically redeploy
```

## Environment Variables (Optional)

If you need to add API keys or secrets:

1. Go to Railway dashboard
2. Click on your project
3. Go to "Variables" tab
4. Add your environment variables
5. Redeploy

## Cost

Railway offers:
- $5 free credit per month
- Pay-as-you-go after that
- This simple API should stay within free tier for light usage

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: Create issues in your repo
