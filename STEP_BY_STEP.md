# Step-by-Step Railway Deployment

## ✅ Checklist

- [ ] Install Xcode Command Line Tools
- [ ] Verify Git works
- [ ] Install Python (if needed)
- [ ] Test app locally
- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Deploy on Railway
- [ ] Test live API

---

## Step 1: Install Xcode Command Line Tools ⏳

**What you need to do:**

A popup should have appeared on your screen asking to install command line developer tools.

1. Click "Install" button
2. Click "Agree" to the license
3. Wait 5-10 minutes for download and installation
4. When done, come back here and tell me "Xcode is installed"

**Why we need this:** Git (version control) requires these tools to work on macOS.

---

## Step 2: Verify Installation

Once Xcode tools are installed, run this command in terminal:

```bash
git --version
```

You should see something like: `git version 2.x.x`

Then run:
```bash
python3 --version
```

You should see something like: `Python 3.x.x`

**If Python is not found:**
- Download from: https://www.python.org/downloads/
- Install the macOS installer
- Run the command again

---

## Step 3: Set Up Local Environment

Run these commands one by one:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

You should see packages installing (Flask, requests, gunicorn).

---

## Step 4: Test Locally

Start the server:

```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

**Open a new terminal tab** (Command + T) and test:

```bash
curl http://localhost:5000/health
```

Should return: `{"status":"healthy"}`

Test the book search:
```bash
curl "http://localhost:5000/api/books?author=Isaac%20Asimov"
```

Should return JSON with books!

Press `Ctrl + C` in the first terminal to stop the server.

---

## Step 5: Create GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - Repository name: `book-finder-api`
   - Description: "REST API to search books by author"
   - Keep it **Public**
   - **DO NOT** check "Add a README file"
   - **DO NOT** check "Add .gitignore"
   - **DO NOT** choose a license
3. Click "Create repository"

**Keep this page open!** You'll need the commands shown.

---

## Step 6: Configure Git (First Time Only)

If this is your first time using Git, set your identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Use the same email as your GitHub account.

---

## Step 7: Push Code to GitHub

Run these commands in your project directory:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Book Finder API"

# Rename branch to main
git branch -M main

# Add GitHub as remote (REPLACE with your URL from GitHub)
git remote add origin https://github.com/YOUR_USERNAME/book-finder-api.git

# Push to GitHub
git push -u origin main
```

**Important:** Replace `YOUR_USERNAME` with your actual GitHub username in the `git remote add` command.

**If asked for credentials:**
- Username: Your GitHub username
- Password: You need a Personal Access Token (not your password)

**To create a token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "Railway Deployment"
4. Check the "repo" checkbox
5. Click "Generate token" at bottom
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

---

## Step 8: Verify on GitHub

1. Go to: https://github.com/YOUR_USERNAME/book-finder-api
2. You should see all your files there!
3. Check that these files exist:
   - app.py
   - Procfile
   - requirements.txt
   - runtime.txt
   - README.md

---

## Step 9: Deploy on Railway

1. Go to: https://railway.app
2. Click "Login" button (top right)
3. Click "Login with GitHub"
4. Authorize Railway to access your GitHub
5. Click "New Project" (big button in center)
6. Select "Deploy from GitHub repo"
7. Find and click on `book-finder-api`
8. Click "Deploy Now"

**Watch the deployment:**
- You'll see logs showing the build process
- Wait for "Success" message (1-2 minutes)

---

## Step 10: Get Your API URL

1. In Railway dashboard, click on your project
2. Click on the "Settings" tab
3. Scroll down to "Networking" section
4. Click "Generate Domain"
5. Copy the URL (something like: `book-finder-api-production.up.railway.app`)

---

## Step 11: Test Your Live API! 🎉

Replace `YOUR_DOMAIN` with your actual Railway domain:

```bash
# Test health endpoint
curl https://YOUR_DOMAIN.up.railway.app/health

# Test API documentation
curl https://YOUR_DOMAIN.up.railway.app/

# Search for books
curl "https://YOUR_DOMAIN.up.railway.app/api/books?author=Isaac%20Asimov"
```

Or open in your browser:
```
https://YOUR_DOMAIN.up.railway.app/
```

---

## 🎊 You're Done!

Your API is now live on the internet! You can:

- Share the URL with anyone
- Use it in other projects
- Add more features and push updates

**To update your API later:**

```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push

# Railway automatically redeploys!
```

---

## Need Help?

If you get stuck at any step, tell me:
1. Which step number you're on
2. What command you ran
3. What error message you see (if any)

I'll help you fix it!
