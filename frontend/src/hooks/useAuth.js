import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react'
import { useState, useEffect } from 'react'

export function useAuth() {
  const { isSignedIn, isLoaded } = useClerkAuth()
  const { user } = useUser()
  const [userRole, setUserRole] = useState(null)

  useEffect(() => {
    if (user && user.publicMetadata) {
      setUserRole(user.publicMetadata.role || 'Viewer')
    }
  }, [user])

  const hasPermission = (requiredRole) => {
    const roleHierarchy = {
      'Viewer': 1,
      'Geotechnical Engineer': 2,
      'Operations Manager': 3,
      'Safety Manager': 4,
      'System Administrator': 5
    }

    const currentRoleLevel = roleHierarchy[userRole] || 1
    const requiredRoleLevel = roleHierarchy[requiredRole] || 1

    return currentRoleLevel >= requiredRoleLevel
  }

  const canAccess = (feature) => {
    const featurePermissions = {
      'dashboard': 'Viewer',
      'alerts': 'Geotechnical Engineer',
      'alert_config': 'Safety Manager',
      'sensors': 'Geotechnical Engineer',
      'imagery': 'Geotechnical Engineer',
      'settings': 'Operations Manager',
      'system_admin': 'System Administrator'
    }

    const requiredRole = featurePermissions[feature] || 'System Administrator'
    return hasPermission(requiredRole)
  }

  const getUserInfo = () => {
    if (!user) return null

    return {
      id: user.id,
      name: user.fullName || user.firstName || 'User',
      email: user.primaryEmailAddress?.emailAddress || '',
      role: userRole,
      avatar: user.profileImageUrl,
      lastSignIn: user.lastSignInAt
    }
  }

  return {
    isAuthenticated: isSignedIn,
    isLoading: !isLoaded,
    user: getUserInfo(),
    userRole,
    hasPermission,
    canAccess
  }
}