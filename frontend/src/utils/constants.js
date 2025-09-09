// API endpoints
export const API_ENDPOINTS = {
  PREDICTIONS: '/predictions',
  RECENT_PREDICTIONS: '/predictions/recent',
  PREDICT: '/predict',
  ALERTS: '/alerts',
  RECENT_ALERTS: '/alerts/recent',
  SENSORS: '/sensors',
  SENSOR_DATA: '/sensors/data',
  DASHBOARD_STATS: '/dashboard/stats',
  MAP_OVERLAY: '/map/risk-overlay'
}

// Risk levels
export const RISK_LEVELS = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High'
}

// Risk colors
export const RISK_COLORS = {
  [RISK_LEVELS.LOW]: '#27ae60',
  [RISK_LEVELS.MEDIUM]: '#f39c12',
  [RISK_LEVELS.HIGH]: '#e74c3c'
}

// Alert types
export const ALERT_TYPES = {
  EMAIL: 'email',
  SMS: 'sms',
  BROWSER: 'browser'
}

// Sensor types
export const SENSOR_TYPES = {
  DISPLACEMENT: 'displacement',
  STRAIN: 'strain',
  PORE_PRESSURE: 'pore_pressure',
  VIBRATION: 'vibration'
}

// Time ranges
export const TIME_RANGES = {
  HOUR: { value: 1, label: 'Last Hour' },
  SIX_HOURS: { value: 6, label: 'Last 6 Hours' },
  DAY: { value: 24, label: 'Last 24 Hours' },
  WEEK: { value: 168, label: 'Last Week' }
}

// Chart configurations
export const CHART_CONFIG = {
  ANIMATION_DURATION: 1000,
  REFRESH_INTERVAL: 30000, // 30 seconds
  MAX_DATA_POINTS: 100,
  COLORS: {
    PRIMARY: '#ff6b35',
    SECONDARY: '#f7931e',
    SUCCESS: '#27ae60',
    WARNING: '#f39c12',
    DANGER: '#e74c3c',
    INFO: '#3498db'
  }
}

// Map configuration
export const MAP_CONFIG = {
  DEFAULT_CENTER: { lat: 28.6139, lng: 77.2090 },
  DEFAULT_ZOOM: 15,
  MIN_ZOOM: 10,
  MAX_ZOOM: 20,
  MARKER_ICONS: {
    LOW_RISK: '🟢',
    MEDIUM_RISK: '🟡',
    HIGH_RISK: '🔴'
  }
}

// File upload limits
export const UPLOAD_LIMITS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: ['image/jpeg', 'image/jpg', 'image/png'],
  MAX_FILES: 10
}

// Dashboard refresh intervals
export const REFRESH_INTERVALS = {
  DASHBOARD: 30000,    // 30 seconds
  SENSORS: 60000,      // 1 minute
  ALERTS: 120000,      // 2 minutes
  PREDICTIONS: 45000   // 45 seconds
}

// User roles
export const USER_ROLES = {
  ADMIN: 'System Administrator',
  SAFETY_MANAGER: 'Safety Manager',
  OPERATIONS_MANAGER: 'Operations Manager',
  ENGINEER: 'Geotechnical Engineer',
  VIEWER: 'Viewer'
}

// System settings
export const SYSTEM_SETTINGS = {
  SESSION_WARNING_TIME: 300000, // 5 minutes before expiry
  AUTO_LOGOUT_TIME: 1800000,    // 30 minutes
  NOTIFICATION_DURATION: 5000,   // 5 seconds
  DEBOUNCE_DELAY: 300           // 300ms
}

export default {
  API_ENDPOINTS,
  RISK_LEVELS,
  RISK_COLORS,
  ALERT_TYPES,
  SENSOR_TYPES,
  TIME_RANGES,
  CHART_CONFIG,
  MAP_CONFIG,
  UPLOAD_LIMITS,
  REFRESH_INTERVALS,
  USER_ROLES,
  SYSTEM_SETTINGS
}