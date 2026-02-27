# Frontend Setup & Launch Guide

## Quick Start

### Step 1: Install Dependencies

```bash
cd frontend/hextech-insights (1)
npm install
```

This will install:
- React 19.2.4
- React Router 7.13
- Recharts 3.7 (for charts)
- TypeScript
- Vite 6.2 (build tool)
- Tailwind CSS (via imports)

### Step 2: Start Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

### Step 3: Verify Backend Connection

Before using the app, ensure the FastAPI backend is running:

```bash
# In another terminal at project root:
.venv/Scripts/python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8001
```

Backend accessible at: **http://127.0.0.1:8001**
Swagger API docs at: **http://127.0.0.1:8001/docs**

---

## Frontend Architecture

### Pages

1. **Dashboard** (`pages/AnalyticsDashboard.tsx`)
   - Main analytics overview
   - Player stats and metrics
   
2. **Model Dashboard** (`pages/ModelDashboard.tsx`)
   - All 4 ML model status
   - System health metrics
   - Model launch buttons

3. **Predictions** (`pages/Predictions.tsx`)
   - Match outcome prediction
   - Team composition analyzer
   - Win probability forecasting
   - **CONNECTED TO BACKEND** ✅

4. **Player Profile** (`pages/Profile.tsx`)
   - Player statistics
   - Match history
   - Progression tracking

### API Integration

The frontend communicates with 4 model groups:

#### Services (`services/api.ts`)

- **matchOutcomeAPI** - 4 variants (early/full/strict/cascade)
- **rankAPI** - Rank classification
- **progressionAPI** - Win rate progression
- **smurfAPI** - Smurf detection
- **healthAPI** - Backend health check

#### Environment Variables

Configure in `.env.local`:
```
VITE_API_BASE_URL=http://127.0.0.1:8001
GEMINI_API_KEY=your_key_here
```

---

## Build for Production

```bash
npm run build
```

This creates an optimized bundle in the `dist/` folder.

To preview production build:
```bash
npm run preview
```

---

## Features Implemented

✅ **Predictions Page**
- Connected to `POST /api/v1/match-outcome/predict/full`
- Displays win probability gauge 
- Real-time confidence scores
- Team composition analysis

🔄 **Other Pages** - Ready for API integration:
- Model Dashboard - Call `/api/v1/match-outcome/models` to list available variants
- Profile Page - Integrate rank/progression/smurf endpoints
- Analytics Dashboard - Fetch aggregated player metrics

---

## Testing the Integration

### Test the API from Frontend

Open browser console at http://localhost:5173 and run:

```javascript
// Test match outcome prediction
const payload = {
  ally_kills: 25,
  ally_deaths: 8,
  ally_gpm: 430,
  ally_xpm: 520,
  ally_total_gold: 75000,
  ally_objectives: 12,
  enemy_kills: 18,
  enemy_deaths: 15,
  enemy_gpm: 380,
  enemy_xpm: 450,
  enemy_total_gold: 65000,
  enemy_objectives: 8,
  game_duration_minutes: 32,
  dragons_taken: 2,
  barons_taken: 0,
};

fetch('http://127.0.0.1:8001/api/v1/match-outcome/predict/full', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
.then(r => r.json())
.then(d => console.log('Prediction:', d));
```

---

## Project Structure

```
frontend/
├── hextech-insights (1)/          # Main React app
│   ├── src/
│   │   ├── pages/                 # Page components
│   │   │   ├── AnalyticsDashboard.tsx
│   │   │   ├── ModelDashboard.tsx
│   │   │   ├── Predictions.tsx    # ✅ Connected to backend
│   │   │   └── Profile.tsx
│   │   ├── components/            # Reusable components
│   │   ├── services/
│   │   │   └── api.ts             # API client (TypeScript)
│   │   ├── App.tsx                # Router config
│   │   ├── index.tsx              # Entry point
│   │   └── types.ts               # TypeScript definitions
│   ├── .env.local                 # Environment config
│   ├── package.json               # Dependencies
│   ├── tsconfig.json              # TypeScript config
│   ├── vite.config.ts             # Build config
│   └── index.html                 # HTML template
├── FRONTEND_DEMO.html             # Design mockup (reference)
└── ...other page mockups/
```

---

## Next Steps

1. Run `npm install` to install dependencies
2. Run `npm run dev` to start development server
3. Visit http://localhost:5173
4. Click "Run Analysis" on Predictions page to test API connection
5. Watch the gauge update with real-time predictions!

---

## Troubleshooting

**Issue: CORS error**
- Solution: Ensure backend is running with CORS middleware enabled ✅ (already added)

**Issue: Cannot find modules**
- Solution: Run `npm install` first

**Issue: Backend not responding**
- Check backend is running on http://127.0.0.1:8001
- Verify with: `curl http://127.0.0.1:8001/health`

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend Framework | React 19 + TypeScript |
| Build Tool | Vite 6.2 |
| Styling | Tailwind CSS |
| Routing | React Router 7 |
| Charts | Recharts 3.7 |
| API Client | Fetch API (built custom service) |
| Backend | FastAPI + Python (connected ✅) |

