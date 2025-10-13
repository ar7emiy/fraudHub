# Frontend Quick Start Guide

## Installation Steps

### 1. Navigate to Frontend Directory
```bash
cd fraud-detection-dashboard/frontend
```

### 2. Install Dependencies
```bash
npm install
```

This will install:
- React 18
- Vite (build tool)
- Tailwind CSS
- Axios (API calls)
- Lucide React (icons)

### 3. Start Development Server
```bash
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

### 4. Verify Backend is Running

Open a separate terminal and ensure backend is running:
```bash
cd fraud-detection-dashboard/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

Backend should show:
```
INFO:__main__:Starting Flask API server on 0.0.0.0:5000
```

### 5. Open Dashboard

Navigate to: http://localhost:5173

You should see:
- Navy blue header with "Fraud Detection Dashboard"
- Filter bar with dropdowns
- Entity list on the left (40 entities)
- "Select an entity from the list" message on the right

## First Use

1. Click any entity in the left list
2. Right panel loads entity details
3. View risk scores, fraud rules, connections, claims
4. Change investigation status from dropdown
5. Use filter bar to narrow entity list
6. Click "Refresh Data" to reload from backend

## Troubleshooting

### "Cannot connect to backend"
- Ensure backend is running on port 5000
- Check http://localhost:5000/api/health in browser
- Should return: {"success": true, "message": "API is running"}

### Blank white screen
- Open browser console (F12)
- Check for JavaScript errors
- Verify all npm packages installed: npm install

### Styles look wrong
- Ensure Tailwind CSS built properly
- Restart dev server: Ctrl+C then npm run dev

### Data not loading
- Check browser Network tab (F12)
- Look for failed API calls
- Verify backend responds to: http://localhost:5000/api/entities

## Expected Behavior

### Entity List (Left Panel)
- Shows 40 entities by default
- Sorted by risk score (highest first)
- Click to select entity
- Selected entity highlighted in light blue
- Status badges colored by status

### Entity Detail (Right Panel)
- Shows when entity selected
- 7 metric cards at top
- Scrollable tables below
- Status dropdown updates immediately
- All tables show real data from backend

### Filters
- Entity Type: Filters by Doctor, Lawyer, etc.
- Min Risk Score: Slider from 0-100
- Status: Filters by investigation status
- All filters apply immediately

### Performance
- Initial load: 1-2 seconds
- Entity selection: <100ms
- Status update: <500ms
- Filter change: <200ms

## Development Mode Features

- Hot Module Replacement (instant updates on code changes)
- React DevTools support
- Detailed error messages in console
- Source maps for debugging

## Next Steps

1. Test all filters
2. Select different entities
3. Update investigation statuses
4. Verify all tables display correctly
5. Test refresh button
6. Review network connections
7. Examine fraud rules

## File Structure Reference

```
frontend/
├── src/
│   ├── components/       # All React components
│   ├── services/         # API communication
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # React entry point
│   └── index.css        # Global styles
├── public/
│   └── index.html       # HTML template
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
└── tailwind.config.js   # Tailwind theme
```

All frontend code is ready to use. No additional configuration needed.