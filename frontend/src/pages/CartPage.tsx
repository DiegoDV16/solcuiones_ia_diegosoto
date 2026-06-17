import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ShoppingCart, Trash2, Plus, Minus, ArrowRight, AlertCircle } from 'lucide-react'

interface CartItem {
  sku: string
  name: string
  price: number
  quantity: number
  image: string
}

export default function CartPage() {
  const [items, setItems] = useState<CartItem[]>(() => {
    try {
      return JSON.parse(sessionStorage.getItem('cart') || '[]')
    } catch {
      return []
    }
  })

  const updateQty = (sku: string, delta: number) => {
    setItems((prev) => {
      const next = prev.map((i) =>
        i.sku === sku ? { ...i, quantity: Math.max(1, i.quantity + delta) } : i
      )
      sessionStorage.setItem('cart', JSON.stringify(next))
      return next
    })
  }

  const removeItem = (sku: string) => {
    setItems((prev) => {
      const next = prev.filter((i) => i.sku !== sku)
      sessionStorage.setItem('cart', JSON.stringify(next))
      return next
    })
  }

  const total = items.reduce((sum, i) => sum + i.price * i.quantity, 0)
  const formatPrice = (p: number) => `$${p.toLocaleString('es-CL')} CLP`

  if (items.length === 0) {
    return (
      <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-20 text-center">
        <ShoppingCart size={64} className="mx-auto text-secondary-200 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Tu Carrito está Vacío</h1>
        <p className="text-secondary-400 mb-6">Agrega productos desde el catálogo para empezar.</p>
        <Link to="/" className="btn-primary inline-flex items-center gap-2">
          Ir a la Tienda <ArrowRight size={16} />
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <ShoppingCart size={24} /> Tu Carrito ({items.length} productos)
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          {items.map((item) => (
            <div key={item.sku} className="card flex gap-4 p-4">
              <div className="bg-secondary-50 rounded-lg w-20 h-20 flex items-center justify-center shrink-0">
                <span className="font-mono text-[10px] text-secondary-300">{item.sku}</span>
              </div>
              <div className="flex-1 min-w-0">
                <Link to={`/producto/${item.sku}`} className="font-semibold text-sm hover:text-primary block truncate">
                  {item.name}
                </Link>
                <p className="text-sm font-bold mt-1">{formatPrice(item.price)}</p>
                <div className="flex items-center gap-3 mt-2">
                  <button onClick={() => updateQty(item.sku, -1)} className="p-1 rounded border border-outline hover:bg-secondary-50">
                    <Minus size={14} />
                  </button>
                  <span className="text-sm font-medium w-6 text-center">{item.quantity}</span>
                  <button onClick={() => updateQty(item.sku, 1)} className="p-1 rounded border border-outline hover:bg-secondary-50">
                    <Plus size={14} />
                  </button>
                  <button onClick={() => removeItem(item.sku)} className="ml-auto p-1 text-red-500 hover:bg-red-50 rounded">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="lg:col-span-1">
          <div className="card p-6 space-y-4 sticky top-24">
            <h3 className="font-semibold">Resumen de Compra</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-secondary-400">Subtotal</span>
                <span>{formatPrice(total)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-400">Despacho</span>
                <span className="text-tertiary-600">Gratis</span>
              </div>
              <div className="border-t border-outline pt-2 flex justify-between font-bold text-base">
                <span>Total</span>
                <span>{formatPrice(total)}</span>
              </div>
            </div>
            <Link
              to="/ordenes"
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              Ir a Pagar <ArrowRight size={16} />
            </Link>
            <p className="text-[10px] text-secondary-400 flex items-center gap-1 justify-center">
              <AlertCircle size={12} /> Stock verificado al momento de la compra
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
