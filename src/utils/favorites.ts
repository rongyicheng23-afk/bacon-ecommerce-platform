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
  return nextIds
}
