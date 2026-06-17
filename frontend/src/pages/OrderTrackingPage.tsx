import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Package, Search, ChevronRight, Clock, MapPin, CheckCircle, Truck } from 'lucide-react'
import { trackOrder } from '../api/client'
import type { OrderTracking } from '../types'

const STATUS_ICONS: Record<string, React.ReactNode> = {
  confirmada: <CheckCircle size={16} className="text-primary" />,
  preparacion: <Truck size={16} className="text-yellow-500" />,
  listo: <MapPin size={16} className="text-tertiary-500" />,
}

export default function OrderTrackingPage() {
  const [orderId, setOrderId] = useState('')
  const [tracking, setTracking] = useState<OrderTracking | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleTrack = async () => {
    const id = parseInt(orderId)
    if (!id) return
    setLoading(true)
    setError('')
    try {
      const data = await trackOrder(id)
      setTracking(data)
    } catch {
      setError('Orden no encontrada. Verifica el número.')
    }
    setLoading(false)
  }

  const formatPrice = (p: number) => `$${p.toLocaleString('es-CL')} CLP`

  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Package size={24} /> Seguimiento de Órdenes
      </h1>

      <div className="card p-6 mb-8">
        <div className="flex gap-3 max-w-md">
          <input
            type="number"
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleTrack()}
            placeholder="Número de orden (ej: 1)"
            className="input flex-1"
          />
          <button onClick={handleTrack} disabled={loading} className="btn-primary flex items-center gap-2">
            <Search size={16} /> {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </div>

      {tracking && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="card p-6">
              <h3 className="font-semibold mb-4">Estado de la Orden #{tracking.order.id}</h3>
              <div className="space-y-4">
                {tracking.tracking.map((step, i) => (
                  <div key={step.estado} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 rounded-full bg-secondary-50 flex items-center justify-center">
                        {STATUS_ICONS[step.estado] || <Clock size={16} />}
                      </div>
                      {i < tracking.tracking.length - 1 && (
                        <div className="w-px h-8 bg-outline mt-1" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{step.descripcion}</p>
                      <p className="text-[10px] text-secondary-400 font-mono">{step.fecha}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card p-6">
              <h3 className="font-semibold mb-4">Productos</h3>
              <div className="space-y-3">
                {tracking.items.map((item) => (
                  <div key={item.sku} className="flex items-center justify-between text-sm">
                    <div>
                      <Link to={`/producto/${item.sku}`} className="hover:text-primary">
                        {item.producto}
                      </Link>
                      <p className="text-[10px] text-secondary-400 font-mono">{item.sku} x{item.cantidad}</p>
                    </div>
                    <span className="font-mono text-xs">{formatPrice(item.precio_unitario * item.cantidad)}</span>
                  </div>
                ))}
              </div>
              <div className="border-t border-outline mt-4 pt-3 flex justify-between font-bold">
                <span>Total</span>
                <span>{formatPrice(tracking.order.total)}</span>
              </div>
            </div>
          </div>

          <div className="lg:col-span-1 space-y-4">
            <div className="card p-6">
              <h4 className="font-mono text-[10px] text-secondary-400 uppercase tracking-wider mb-2">Sucursal</h4>
              <p className="font-semibold text-sm">{tracking.order.branch_codigo}</p>
              <p className="text-xs text-secondary-400">{tracking.order.branch_nombre}</p>
              <p className="text-xs text-secondary-400">{tracking.order.direccion}</p>
            </div>

            {tracking.recommendations.length > 0 && (
              <div className="card p-6">
                <h4 className="font-semibold text-sm mb-3">📦 Recomendados para ti</h4>
                <div className="space-y-3">
                  {tracking.recommendations.map((rec) => (
                    <Link
                      key={rec.sku}
                      to={`/producto/${rec.sku}`}
                      className="block text-sm hover:text-primary transition-colors"
                    >
                      <p className="font-medium truncate">{rec.nombre}</p>
                      <p className="text-[10px] text-secondary-400">{rec.reason}</p>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {!tracking && !error && (
        <div className="text-center py-16 text-secondary-400">
          <Package size={48} className="mx-auto mb-3 text-secondary-200" />
          <p>Ingresa tu número de orden para ver el estado.</p>
        </div>
      )}
    </div>
  )
}
