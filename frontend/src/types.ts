export interface Product {
  sku: string
  nombre: string
  descripcion: string | null
  precio_lista: number
  descuento_efectivo: number
  categoria: string | null
  total_stock: number
  inventory: InventoryItem[]
}

export interface InventoryItem {
  branch_codigo: string
  branch_nombre: string
  direccion: string
  region: string
  comuna: string
  cantidad: number
}

export interface Category {
  id: number
  nombre: string
}

export interface Branch {
  id: number
  codigo: string
  nombre: string
  region: string
  comuna: string
  direccion: string | null
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ProductCardItem {
  sku: string
  nombre: string
  precio_lista: number
  descuento_efectivo: number
  total_stock: number
  categoria: string | null
}

export const CATEGORY_ICONS: Record<string, string> = {
  procesadores: 'cpu',
  video: 'gpu',
  ram: 'memory',
  almacenamiento: 'storage',
  placas: 'motherboard',
  fuentes: 'psu',
  gabinetes: 'case',
  refrigeracion: 'cooler',
  perifericos: 'mouse',
  monitores: 'monitor',
  accesorios: 'accessory',
}

export interface Recommendation {
  sku: string
  nombre: string
  precio_lista: number
  descuento_efectivo: number
  categoria: string
  total_stock: number
  reason: string
}

export interface OrderTracking {
  order: {
    id: number
    fecha: string
    cliente_nombre: string | null
    total: number
    branch_codigo: string
    branch_nombre: string
    region: string
    comuna: string
    direccion: string
  }
  items: {
    sku: string
    cantidad: number
    precio_unitario: number
    descuento: number
    producto: string
  }[]
  tracking: {
    estado: string
    fecha: string
    descripcion: string
  }[]
  recommendations: Recommendation[]
}

export interface BundleRecommendation {
  budget: number
  total: number
  remaining: number
  items: Product[]
}
