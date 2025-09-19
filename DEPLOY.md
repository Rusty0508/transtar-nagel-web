# 🚀 Deployment Guide

## Option 1: Deploy to Render (Recommended - Free)

1. **Fork/Clone the repository** to your GitHub account

2. **Sign up** at [render.com](https://render.com)

3. **Create New Web Service:**
   - Connect your GitHub account
   - Select the `transtar-nagel-web` repository
   - Configure:
     - **Name**: `transtar-nagel`
     - **Region**: Choose nearest
     - **Branch**: `main`
     - **Root Directory**: (leave empty)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `cd web_app && python app.py`

4. **Environment Variables** (if needed):
   - Click "Advanced" → Add Environment Variable
   - Add any required variables

5. **Deploy** - Click "Create Web Service"

Your app will be available at: `https://transtar-nagel.onrender.com`

## Option 2: Deploy to Railway

1. **Sign up** at [railway.app](https://railway.app)

2. **New Project** → Deploy from GitHub repo

3. **Select** `transtar-nagel-web` repository

4. **Configure**:
   - Add Start Command: `cd web_app && python app.py`
   - Railway will auto-detect Python and install requirements

5. **Generate Domain** in Settings

## Option 3: Deploy to Heroku

1. **Create** `Procfile` in root:
```
web: cd web_app && python app.py
```

2. **Create** `runtime.txt`:
```
python-3.11.0
```

3. **Deploy via Heroku CLI**:
```bash
heroku create transtar-nagel
git push heroku main
```

## Option 4: Deploy to PythonAnywhere

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload files** via Web UI or Git

3. **Create virtual environment**:
```bash
mkvirtualenv transtar --python=python3.9
pip install -r requirements.txt
```

4. **Configure WSGI** file to point to `web_app/app.py`

## Option 5: Deploy to Vercel (Serverless)

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
vercel
```

3. Follow prompts and select Python as runtime

## Option 6: Deploy to Google Cloud Run

1. **Create** `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
WORKDIR /app/web_app
CMD ["python", "app.py"]
```

2. **Build and deploy**:
```bash
gcloud run deploy --source .
```

## Option 7: Deploy to Replit

1. **Import** from GitHub at [replit.com](https://replit.com)

2. **Configure** `.replit` file:
```
run = "cd web_app && python app.py"
```

3. **Click Run**

## Local Development

```bash
# Clone repository
git clone https://github.com/Rusty0508/transtar-nagel-web.git
cd transtar-nagel-web

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
cd web_app
python app.py
```

## Notes

- Most free tiers have limitations (CPU, RAM, storage)
- For production use, consider paid plans
- Files uploaded via web interface are temporary
- Consider using cloud storage for persistent files

## Recommended: Render.com

✅ Free tier available
✅ Auto-deploy from GitHub
✅ Custom domains supported
✅ SSL included
✅ No credit card required

---

**Support**: Open an issue on GitHub if you need help!