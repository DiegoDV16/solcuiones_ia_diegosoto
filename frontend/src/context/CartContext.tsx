import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

interface CartItem {
  sku: string
  name: string
  price: number
  quantity: number
}

interface CartContextType {
  items: CartItem[]
  count: number
  total: number
  add: (sku: string, name: string, price: number) => void
  updateQty: (sku: string, delta: number) => void
  remove: (sku: string) => void
  clear: () => void
}

const CartContext = createContext<CartContextType | null>(null)

function loadCart(): CartItem[] {
  try {
    return JSON.parse(sessionStorage.getItem('cart') || '[]')
  } catch {
    return []
  }
}

function saveCart(items: CartItem[]) {
  sessionStorage.setItem('cart', JSON.stringify(items))
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>(loadCart)

  useEffect(() => {
    saveCart(items)
  }, [items])

  const add = (sku: string, name: string, price: number) => {
    setItems((prev) => {
      const found = prev.find((i) => i.sku === sku)
      if (found) {
        return prev.map((i) => (i.sku === sku ? { ...i, quantity: i.quantity + 1 } : i))
      }
      return [...prev, { sku, name, price, quantity: 1 }]
    })
  }

  const updateQty = (sku: string, delta: number) => {
    setItems((prev) =>
      prev.map((i) => (i.sku === sku ? { ...i, quantity: Math.max(1, i.quantity + delta) } : i))
    )
  }

  const remove = (sku: string) => {
    setItems((prev) => prev.filter((i) => i.sku !== sku))
  }

  const clear = () => setItems([])

  const count = items.reduce((s, i) => s + i.quantity, 0)
  const total = items.reduce((s, i) => s + i.price * i.quantity, 0)

  return (
    <CartContext.Provider value={{ items, count, total, add, updateQty, remove, clear }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart(): CartContextType {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
