# 🚀 Deployment Guide

This guide covers multiple deployment options for the Smart Receipt Processor.

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- ✅ **Gemini API Key** from [Google AI Studio](https://ai.google.dev/)
- ✅ **GitHub account** for code hosting
- ✅ **Deployment platform account** (Vercel, Railway, Heroku, etc.)

## 🌟 Option 1: Vercel (Recommended)

### Quick Deploy Button
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/smart-receipt-processor)

### Manual Setup

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial release"
   git branch -M main
   git remote add origin https://github.com/yourusername/smart-receipt-processor.git
   git push -u origin main
   ```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Set environment variable: `GEMINI_API_KEY=your_api_key`
   - Deploy!

### GitHub Actions Setup (Optional)

If you want automatic deployment, add these secrets to your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   ```
   VERCEL_TOKEN=your_vercel_token
   ORG_ID=your_vercel_org_id  
   PROJECT_ID=your_vercel_project_id
   ```

To get these values:
- **VERCEL_TOKEN**: Generate at [vercel.com/account/tokens](https://vercel.com/account/tokens)
- **ORG_ID & PROJECT_ID**: Run `vercel project list` in your project directory

## 🚂 Option 2: Railway

1. **Connect GitHub account** at [railway.app](https://railway.app)
2. **Deploy from GitHub** repository
3. **Add environment variable**: `GEMINI_API_KEY=your_api_key`
4. **Deploy automatically**

## 🟣 Option 3: Heroku

1. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Add environment variable:**
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

## 💻 Option 4: Local Production

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export GEMINI_API_KEY=your_api_key
   export FLASK_ENV=production
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn --bind 0.0.0.0:8000 wsgi:application
   ```

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key for AI processing |
| `SECRET_KEY` | 🔶 Recommended | Flask secret key (auto-generated if not set) |
| `FLASK_ENV` | 🔶 Optional | Set to `production` for production mode |

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors:**
- Ensure all dependencies are in `requirements.txt`
- Check that `src/` directory is included in deployment

**2. API Key Issues:**
- Verify `GEMINI_API_KEY` is set correctly
- Test API key with Google AI Studio

**3. File Upload Issues:**
- Ensure `uploads/` and `results/` directories exist
- Check file permissions in production

### Debugging

Enable debug mode locally:
```bash
export FLASK_ENV=development
python app.py
```

Check logs in production:
- **Vercel**: View function logs in dashboard
- **Railway**: Check deployment logs
- **Heroku**: Use `heroku logs --tail`

## 🎯 Production Considerations

### Performance
- ✅ Uses Gunicorn WSGI server
- ✅ Optimized for serverless deployment
- ✅ Efficient memory usage

### Security
- ✅ Environment-based configuration
- ✅ Secure secret management
- ✅ Input validation and sanitization

### Scalability
- ✅ Stateless design
- ✅ Horizontal scaling ready
- ✅ CDN-friendly static assets

## 📊 Monitoring

After deployment, monitor:
- Response times
- Error rates  
- API usage
- Storage usage

Most platforms provide built-in monitoring dashboards.

---

🎉 **Smart Receipt Processor is now ready for production!**
