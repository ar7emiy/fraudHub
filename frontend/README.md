# Fraud Detection Dashboard - Frontend

React-based frontend dashboard for Workers Compensation Fraud Detection system.

## Prerequisites

- Node.js 16 or higher
- npm or yarn
- Backend API running on http://localhost:5000

## Setup Instructions

### 1. Install Dependencies

```bash
cd fraud-detection-dashboard/frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will start on http://localhost:5173

### 3. Ensure Backend is Running

Before using the frontend, make sure the backend API is running:

```bash
cd ../backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

The backend should be running on http://localhost:5000

## Features

### Entity Risk Rankings
- Sort by risk score, exposure, or claim count
- Filter by entity type, investigation status, and minimum risk score
- Real-time visual indicators for risk levels
- Priority ranking system

### Entity Detail View
- Comprehensive risk score breakdown
- Investigation status management
- Fraud rules triggered
- Network connections analysis
- Associated claims information
- Community membership details

### Color-Coded Risk Indicators
- Red (85+): High risk entities
- Orange (70-84): Medium risk entities
- Yellow (<70): Lower risk entities

### Investigation Status Management
- Not Reviewed (default)
- Under Investigation
- Bad Actor (confirmed fraud)
- Cleared (investigation closed)

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── FilterBar.js
│   │   ├── EntityList.js
│   │   ├── EntityDetail.js
│   │   ├── RiskScoreCards.js
│   │   ├── FraudRulesTable.js
│   │   ├── NetworkConnectionsTable.js
│   │   ├── ClaimsTable.js
│   │   └── CommunityAnalysisTable.js
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Design System

### Colors
- Navy Blue: Primary brand color (headers, titles)
- Light Blue: Interactive elements (buttons, selections)
- Silver: Borders and subtle elements
- White/Gray: Backgrounds

### Typography
- Clean sans-serif font
- Bold headers for hierarchy
- Consistent sizing (14px minimum)

### Components
- Card-based metric displays
- Scrollable tables with sticky headers
- Subtle hover transitions
- Color-coded status badges

## API Integration

The frontend communicates with the backend through REST API calls:

- GET /api/entities - Load entity rankings
- GET /api/entity/{name} - Load entity details
- PUT /api/entity/{name}/status - Update investigation status
- POST /api/reload - Refresh all data

All API calls are handled through the centralized api.js service.

## Development

### Hot Reload
Vite provides instant hot module replacement. Changes to components will reflect immediately without full page reload.

### Adding New Components
1. Create component file in src/components/
2. Import and use in parent component
3. Follow existing naming conventions

### Modifying Styles
- Update tailwind.config.js for color/theme changes
- Use Tailwind utility classes in components
- Custom styles in index.css if needed

## Building for Production

```bash
npm run build
```

Production files will be generated in the dist/ directory.

## Troubleshooting

### Backend Connection Failed
Ensure backend is running on port 5000. Check browser console for CORS errors.

### Styles Not Loading
Run: npm install
Restart dev server: npm run dev

### Components Not Rendering
Check browser console for errors. Verify all dependencies installed correctly.

### Data Not Loading
1. Verify backend API health: http://localhost:5000/api/health
2. Check browser network tab for failed requests
3. Ensure CORS is properly configured in backend

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

Desktop only (minimum width: 1280px)

## Performance Notes

- Entity list virtualization not implemented (acceptable for <1000 entities)
- Manual refresh required for data updates
- Tables have max height with scrolling for large datasets

## Future Enhancements

Tracked in implementation plan:
- Export functionality for network connections
- Interactive network visualization
- Real-time data updates
- Advanced filtering options
- Bulk status updates
- Report generation