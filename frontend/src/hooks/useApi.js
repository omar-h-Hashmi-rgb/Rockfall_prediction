import { useState, useCallback } from 'react'
import api from '../utils/api'

export function useApi() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const request = useCallback(async (method, url, data = null) => {
    try {
      setLoading(true)
      setError(null)
      
      const config = {
        method,
        url,
        ...(data && { data })
      }
      
      const response = await api(config)
      return response
    } catch (err) {
      setError(err.message || 'An error occurred')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const get = useCallback((url) => request('GET', url), [request])
  const post = useCallback((url, data) => request('POST', url, data), [request])
  const put = useCallback((url, data) => request('PUT', url, data), [request])
  const del = useCallback((url) => request('DELETE', url), [request])

  return {
    loading,
    error,
    get,
    post,
    put,
    delete: del
  }
}