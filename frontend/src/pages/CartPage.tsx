import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShoppingCart, Trash2, Plus, Minus, ArrowRight, AlertCircle, CreditCard, Check } from 'lucide-react'
import { getBranches, simulateOrder, createOrder } from '../api/client'
import type { Branch } from '../types'
import { useCart } from '../context/CartContext'

export default function CartPage() {
  const navigate = useNavigate()
  const { items, updateQty, remove, clear, total } = useCart()
  const [showCheckout, setShowCheckout] = useState(false)
  const [branches, setBranches] = useState<Branch[]>([])
  const [selectedBranch, setSelectedBranch] = useState('')
  const [customerName, setCustomerName] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [orderResult, setOrderResult] = useState<{ id: number; total: number } | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getBranches().then(setBranches).catch(() => {})
  }, [])

  const fp = (p: number) => `$${p.toLocaleString('es-CL')} CLP`

  const handleCheckout = async () => {
    if (!selectedBranch || !customerName.trim()) return
    setSubmitting(true)
    setError('')
    try {
      const sim = await simulateOrder({
        branch_code: selectedBranch,
        items: items.map((i) => ({ sku: i.sku, cantidad: i.quantity })),
        cliente_nombre: customerName.trim(),
      })
      const order = await createOrder({
        branch_code: selectedBranch,
        items: items.map((i) => ({ sku: i.sku, cantidad: i.quantity })),
        cliente_nombre: customerName.trim(),
      })
      setOrderResult({ id: order.id || sim.id, total: sim.total || total })
      clear()
    } catch (e) {
      setError('Error al procesar la orden. Intenta de nuevo.')
    }
    setSubmitting(false)
  }

  if (orderResult) {
    return (
      <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-20 text-center">
        <div className="w-16 h-16 bg-tertiary-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <Check size={32} className="text-tertiary-600" />
        </div>
        <h1 className="text-2xl font-bold mb-2">¡Orden Creada!</h1>
        <p className="text-secondary-400 mb-2">N° de orden: <strong>{orderResult.id}</strong></p>
        <p className="text-secondary-400 mb-6">Total: {fp(orderResult.total)}</p>
        <Link to="/ordenes" className="btn-primary inline-flex items-center gap-2">
          Ver Seguimiento <ArrowRight size={16} />
        </Link>
      </div>
    )
  }

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
                <p className="text-sm font-bold mt-1">{fp(item.price)}</p>
                <div className="flex items-center gap-3 mt-2">
                  <button onClick={() => updateQty(item.sku, -1)} className="p-1 rounded border border-outline hover:bg-secondary-50">
                    <Minus size={14} />
                  </button>
                  <span className="text-sm font-medium w-6 text-center">{item.quantity}</span>
                  <button onClick={() => updateQty(item.sku, 1)} className="p-1 rounded border border-outline hover:bg-secondary-50">
                    <Plus size={14} />
                  </button>
                  <button onClick={() => remove(item.sku)} className="ml-auto p-1 text-red-500 hover:bg-red-50 rounded">
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
                <span>{fp(total)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-400">Despacho</span>
                <span className="text-tertiary-600">Gratis</span>
              </div>
              <div className="border-t border-outline pt-2 flex justify-between font-bold text-base">
                <span>Total</span>
                <span>{fp(total)}</span>
              </div>
            </div>

            {!showCheckout ? (
              <button
                onClick={() => setShowCheckout(true)}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <CreditCard size={16} /> Ir a Pagar <ArrowRight size={16} />
              </button>
            ) : (
              <div className="space-y-3 border-t border-outline pt-4">
                <h4 className="text-sm font-semibold">Datos de Envío</h4>
                <input
                  type="text"
                  placeholder="Tu nombre"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="input text-sm w-full"
                />
                <select
                  value={selectedBranch}
                  onChange={(e) => setSelectedBranch(e.target.value)}
                  className="input text-sm w-full"
                >
                  <option value="">Selecciona sucursal</option>
                  {branches.map((b) => (
                    <option key={b.codigo} value={b.codigo}>
                      {b.nombre} - {b.comuna}, {b.region}
                    </option>
                  ))}
                </select>
                {error && <p className="text-xs text-red-500">{error}</p>}
                <button
                  onClick={handleCheckout}
                  disabled={submitting || !selectedBranch || !customerName.trim()}
                  className="btn-primary w-full text-sm disabled:opacity-50"
                >
                  {submitting ? 'Procesando...' : `Confirmar Pago ${fp(total)}`}
                </button>
                <button
                  onClick={() => setShowCheckout(false)}
                  className="text-xs text-secondary-400 hover:text-on-surface w-full text-center"
                >
                  Volver
                </button>
              </div>
            )}

            <p className="text-[10px] text-secondary-400 flex items-center gap-1 justify-center">
              <AlertCircle size={12} /> Stock verificado al momento de la compra
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
