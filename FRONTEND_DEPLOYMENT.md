# Frontend Deployment Guide - Connecting to Render.com Backend

After deploying your backend to Render.com, you need to update your frontend to connect to it.

## Quick Setup

### 1. Create Environment File

Create a `.env` file in the root of your project (same level as `package.json`):

```bash
# .env
VITE_API_BASE_URL=https://your-backend-app.onrender.com
```

**Important:** Replace `your-backend-app` with your actual Render.com backend service URL.

### 2. Update Backend CORS Settings

In your Render.com backend service, add/update the `CORS_ORIGINS` environment variable to include your frontend URL:

**If deploying frontend to Render.com:**
```bash
CORS_ORIGINS=https://your-frontend-app.onrender.com,https://www.your-frontend-app.onrender.com
```

**If deploying frontend to another platform (Vercel, Netlify, etc.):**
```bash
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

**For local development:**
```bash
CORS_ORIGINS=http://localhost:8080,http://localhost:5173,http://localhost:3000
```

**For both production and local:**
```bash
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com,http://localhost:8080,http://localhost:5173
```

## Environment Variables

### Development (.env.local)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Production (.env.production)
```bash
VITE_API_BASE_URL=https://your-backend-app.onrender.com
```

## Testing the Connection

1. Start your frontend development server:
   ```bash
   pnpm dev
   ```

2. Check the browser console for any CORS errors

3. Test the connection by visiting the Connect page and checking if the API calls work

## Common Issues

### CORS Errors

If you see CORS errors in the browser console:
- Make sure your frontend URL is in the backend's `CORS_ORIGINS` environment variable
- Check that the URLs match exactly (including https://)
- Restart your backend service after updating CORS_ORIGINS

### API Connection Failed

If API calls fail:
- Verify `VITE_API_BASE_URL` is set correctly in your `.env` file
- Check that your backend is running and accessible at the URL
- Test the backend health endpoint: `https://your-backend-app.onrender.com/health`
- Check browser Network tab for the actual request URL

### Environment Variable Not Loading

- Make sure `.env` file is in the root directory (same level as `package.json`)
- Restart your development server after creating/updating `.env`
- Vite requires `VITE_` prefix for environment variables
- For production builds, ensure the environment variable is set in your hosting platform

## Deploying Frontend

### Option 1: Render.com

1. Create a new **Static Site** service in Render.com
2. Connect your GitHub repository
3. Set build command: `pnpm install && pnpm build`
4. Set publish directory: `dist`
5. Add environment variable:
   - `VITE_API_BASE_URL=https://your-backend-app.onrender.com`

### Option 2: Vercel

1. Connect your GitHub repository to Vercel
2. Set build command: `pnpm build`
3. Set output directory: `dist`
4. Add environment variable in Vercel dashboard:
   - `VITE_API_BASE_URL=https://your-backend-app.onrender.com`

### Option 3: Netlify

1. Connect your GitHub repository to Netlify
2. Set build command: `pnpm build`
3. Set publish directory: `dist`
4. Add environment variable in Netlify dashboard:
   - `VITE_API_BASE_URL=https://your-backend-app.onrender.com`

## Security Notes

- Never commit `.env` files to version control
- Use `.env.example` as a template (already created)
- For production, set environment variables in your hosting platform's dashboard
- The `.env` file is automatically ignored by `.gitignore`

## Next Steps

1. ✅ Create `.env` file with your backend URL
2. ✅ Update backend `CORS_ORIGINS` in Render.com
3. ✅ Test locally with `pnpm dev`
4. ✅ Deploy frontend to your preferred platform
5. ✅ Test production deployment


