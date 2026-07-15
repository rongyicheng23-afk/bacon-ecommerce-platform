import api from './api'
import type { Address } from '@/utils/addresses'

interface ApiResponse<T> {
  code: string
  info: string
  data: T
}

export const addressService = {
  async list(): Promise<Address[]> {
    const response = await api.get<ApiResponse<Address[]>>('/addresses')
    return response.data.data
  },

  async create(data: Omit<Address, 'id'>): Promise<Address> {
    const response = await api.post<ApiResponse<Address>>('/addresses', {
      name: data.name,
      phone: data.phone,
      detail: data.detail,
      isDefault: data.isDefault ?? false
    })
    return response.data.data
  },

  async update(id: number, data: Partial<Omit<Address, 'id'>>): Promise<Address> {
    const response = await api.put<ApiResponse<Address>>(`/addresses/${id}`, {
      name: data.name,
      phone: data.phone,
      detail: data.detail,
      isDefault: data.isDefault
    })
    return response.data.data
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/addresses/${id}`)
  }
}
