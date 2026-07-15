const favoriteStorageKey = 'favoriteProductIds'

export const readFavoriteIds = () => {
  try {
    const ids = JSON.parse(localStorage.getItem(favoriteStorageKey) || '[]') as number[]
    return Array.isArray(ids) ? ids : []
  } catch {
    return []
  }
}

export const saveFavoriteIds = (ids: number[]) => {
  localStorage.setItem(favoriteStorageKey, JSON.stringify([...new Set(ids)]))
}

export const toggleFavoriteId = (productId: number) => {
  const ids = readFavoriteIds()
  const nextIds = ids.includes(productId)
    ? ids.filter((id) => id !== productId)
    : [productId, ...ids]

  saveFavoriteIds(nextIds)
  // 页面先即时反馈；登录用户再同步到后端，后端会同时写入推荐行为日志。
  if (localStorage.getItem('token')) {
    const request = ids.includes(productId)
      ? api.delete<{ data: number[] }>(`/favorites/${productId}`)
      : api.post<{ data: number[] }>(`/favorites/${productId}`)
    void request.then((response) => saveFavoriteIds(response.data.data || nextIds)).catch(() => undefined)
  }
  return nextIds
}
import api from '@/services/api'
