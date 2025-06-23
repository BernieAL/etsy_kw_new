# Etsy Monitor Frontend

A modern React frontend for the Etsy monitoring tool, built with TypeScript, Tailwind CSS, and React Query.

## 🚀 Features

- **Modern React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Query** for server state management
- **React Router** for navigation
- **Responsive design** with mobile-first approach
- **Error boundaries** for graceful error handling
- **Loading states** and optimistic updates

## 🛠️ Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **Heroicons** - Icon library

## 📦 Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API URL
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   ```
   http://localhost:5173
   ```

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with navigation
│   ├── LoadingSpinner.tsx
│   └── ErrorBoundary.tsx
├── pages/              # Page components
│   └── Dashboard.tsx   # Dashboard page
├── services/           # API services
│   └── api.ts         # API client and endpoints
├── types/              # TypeScript type definitions
│   └── index.ts       # Shared types
├── contexts/           # React contexts
│   └── QueryProvider.tsx
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
└── App.tsx            # Main app component
```

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Development Configuration
VITE_DEV_MODE=true
VITE_ENABLE_LOGGING=true
```

### API Integration

The frontend communicates with the backend API through the `services/api.ts` file. Make sure your backend is running on the URL specified in `VITE_API_URL`.

## 🎨 Styling

This project uses Tailwind CSS with custom components defined in `src/index.css`. The design system includes:

- **Color palette** with primary colors
- **Component classes** for buttons, cards, inputs
- **Responsive utilities** for mobile-first design
- **Custom animations** and transitions

## 📱 Responsive Design

The frontend is fully responsive with:
- **Mobile-first** approach
- **Sidebar navigation** that collapses on mobile
- **Flexible grid layouts** that adapt to screen size
- **Touch-friendly** interface elements

## 🔄 State Management

- **React Query** for server state (API data)
- **React state** for local component state
- **React Router** for navigation state
- **Error boundaries** for error state

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Deploy to VPS

The frontend can be deployed alongside the backend using the existing deployment scripts. The build output will be served by Nginx.

## 🔗 Backend Integration

This frontend is designed to work with the Etsy monitoring backend API. Make sure:

1. **Backend is running** on the correct port
2. **CORS is configured** properly
3. **API endpoints** match the expected structure
4. **Environment variables** are set correctly

## 🎯 Next Steps

- [ ] Complete Rules management page
- [ ] Add Notifications page
- [ ] Implement Settings page
- [ ] Add user authentication
- [ ] Create data visualization components
- [ ] Add real-time updates
- [ ] Implement search and filtering
- [ ] Add export functionality

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript for all new code
3. Add proper error handling
4. Test on mobile devices
5. Update documentation as needed
