import type { Product, Category, Branch } from '../types'

const BASE = '/api'

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `${res.status} ${res.statusText}`)
  }
  return res.json()
}

export async function getProducts(params?: {
  category?: string
  search?: string
}): Promise<Product[]> {
  const q = new URLSearchParams()
  if (params?.category) q.set('category', params.category)
  if (params?.search) q.set('search', params.search)
  const qs = q.toString()
  return fetchJSON(`/products${qs ? `?${qs}` : ''}`)
}

export async function getProduct(sku: string): Promise<Product> {
  return fetchJSON(`/products/${encodeURIComponent(sku)}`)
}

export async function getCategories(): Promise<Category[]> {
  return fetchJSON('/categories')
}

export async function getBranches(): Promise<Branch[]> {
  return fetchJSON('/branches')
}

export async function chatSend(
  message: string,
  sessionId = 'default'
): Promise<{ reply: string; session_id: string }> {
  return fetchJSON('/chat', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
  })
}

export async function chatReset(sessionId = 'default'): Promise<{ status: string }> {
  return fetchJSON(`/chat/reset?session_id=${sessionId}`, { method: 'POST' })
}

export async function simulateOrder(data: {
  branch_code: string
  items: { sku: string; cantidad: number }[]
  cliente_nombre?: string
}) {
  return fetchJSON('/orders/simulate', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function createOrder(data: {
  branch_code: string
  items: { sku: string; cantidad: number }[]
  cliente_nombre?: string
}) {
  return fetchJSON('/orders', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function formatPrice(price: number): string {
  return `$${price.toLocaleString('es-CL')} CLP`
}

export function discountedPrice(lista: number, descuento: number): number {
  return lista - Math.floor(lista * descuento)
}

export function getStockLabel(stock: number): { label: string; className: string } {
  if (stock > 5) return { label: 'In Stock', className: 'chip-instock' }
  if (stock > 0) return { label: 'Low Stock', className: 'chip-lowstock' }
  return { label: 'Out of Stock', className: 'chip-outofstock' }
}
