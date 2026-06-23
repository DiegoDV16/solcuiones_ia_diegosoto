import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Lightbulb, ShoppingCart, TrendingUp, Sparkles } from 'lucide-react'
import ProductCard from '../components/ProductCard'
import { getProducts, getBundleRecommendations } from '../api/client'
import type { Product } from '../types'

export default function RecommendationsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [budget, setBudget] = useState('')
  const [bundle, setBundle] = useState<Product[]>([])
  const [bundleTotal, setBundleTotal] = useState(0)
  const [loadingBundle, setLoadingBundle] = useState(false)

  useEffect(() => {
    getProducts({}).then(setProducts)
  }, [])

  const handleBundle = async () => {
    const b = parseInt(budget.replace(/\./g, ''))
    if (!b || b < 100000) return
    setLoadingBundle(true)
    try {
      const data = await getBundleRecommendations(b)
      setBundle(data.items || [])
      setBundleTotal(data.total || 0)
    } catch {
      setBundle([])
    }
    setLoadingBundle(false)
  }

  const formatPrice = (p: number) => `$${p.toLocaleString('es-CL')} CLP`

  const bestSellers = products.filter((p) => p.total_stock > 5).slice(0, 4)

  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
      <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
        <Lightbulb size={24} className="text-yellow-500" /> Recomendaciones Inteligentes
      </h1>
      <p className="text-secondary-400 text-sm mb-8">
        Sugerencias basadas en tu historial y productos populares en PC Factory.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <section>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp size={18} className="text-primary" /> Más Vendidos
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {bestSellers.map((p) => (
                <ProductCard key={p.sku} product={p} />
              ))}
            </div>
          </section>

          {bundle.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Sparkles size={18} className="text-primary" /> PC Armada para ti
              </h2>
              <div className="bg-primary-50 border border-primary-100 rounded-xl p-4 mb-4">
                <p className="text-sm">
                  Total: <strong>{formatPrice(bundleTotal)}</strong> | Presupuesto: {formatPrice(parseInt(budget.replace(/\./g, '')))}
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {bundle.map((p) => (
                  <ProductCard key={p.sku} product={p} />
                ))}
              </div>
            </section>
          )}
        </div>

        <div className="lg:col-span-1">
          <div className="card p-6 space-y-4 sticky top-24">
            <h3 className="font-semibold flex items-center gap-2">
              <ShoppingCart size={16} /> Arma tu PC
            </h3>
            <p className="text-xs text-secondary-400">
              Ingresa tu presupuesto y te recomendaremos una configuración completa.
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={budget}
                onChange={(e) => setBudget(e.target.value.replace(/[^0-9]/g, ''))}
                placeholder="Ej: 1500000"
                className="input flex-1 text-sm"
              />
            </div>
            <button
              onClick={handleBundle}
              disabled={loadingBundle || !budget}
              className="btn-primary w-full text-sm"
            >
              {loadingBundle ? 'Calculando...' : 'Obtener Recomendación'}
            </button>
            <p className="text-[10px] text-secondary-400">Monto mínimo: $100,000 CLP</p>

            <div className="border-t border-outline pt-4">
              <h4 className="font-mono text-[10px] text-secondary-400 uppercase tracking-wider mb-2">
                ¿Sabías que...?
              </h4>
              <p className="text-xs text-secondary-400">
                Nuestro asistente IA puede ayudarte a elegir los componentes compatibles. 
                <Link to="/asistente" className="text-primary hover:underline ml-1">Pregúntale aquí</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
