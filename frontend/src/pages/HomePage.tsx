import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, ChevronRight, MemoryStick, Cpu, Monitor, HardDrive, Database, ArrowRight } from 'lucide-react'
import ProductCard from '../components/ProductCard'
import { getProducts, getCategories } from '../api/client'
import type { Product, Category } from '../types'

const CATEGORY_MAP: Record<string, { icon: React.ReactNode; label: string }> = {
  procesadores: { icon: <Cpu size={24} />, label: 'CPUs' },
  video: { icon: <Monitor size={24} />, label: 'GPUs' },
  placas: { icon: <Cpu size={24} />, label: 'Motherboards' },
  ram: { icon: <MemoryStick size={24} />, label: 'RAM' },
  almacenamiento: { icon: <HardDrive size={24} />, label: 'Storage' },
}

const PROMOS = [
  {
    sku: 'GPU-NVIDIA-RTX4080-SUPER',
    name: 'NVIDIA GEFORCE RTX 4080 Super OC 16GB GDDR6X',
    original: 1249990,
    discount: 0.10,
    stock: 'In Stock',
  },
  {
    sku: 'CPU-AMD-R7-7800X3D',
    name: 'AMD RYZEN Ryzen 9 7950X3D 16-Core 32-Thread',
    original: 449990,
    discount: 0.05,
    stock: 'In Stock',
  },
  {
    sku: 'RAM-CORSAIR-32GB-DDR5',
    name: 'CORSAIR VENGEANCE 32GB DDR5 6000MHz CL30 RGB Kit',
    original: 129990,
    discount: 0.10,
    stock: 'Low Stock',
  },
  {
    sku: 'SSD-SAMSUNG-2TB-990',
    name: 'SAMSUNG PRO 990 Pro 2TB PCIe 4.0 NVMe M.2',
    original: 199990,
    discount: 0.10,
    stock: 'In Stock',
  },
]

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getProducts(), getCategories()]).then(([prods, cats]) => {
      setProducts(prods)
      setCategories(cats)
      setLoading(false)
    })
  }, [])

  const formatPrice = (p: number) => `$${(p / 1000).toFixed(0)}.{${p % 1000}}`

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-secondary-800 via-secondary-800 to-primary-900 text-white">
        <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-20 lg:py-28">
          <div className="max-w-2xl">
            <h1 className="text-4xl lg:text-5xl font-bold leading-tight mb-4">
              Engineered for<br />Peak Performance
            </h1>
            <p className="text-secondary-200 text-lg mb-8">
              Your destination for high-end PC components and professional workstation builds.
            </p>
            <div className="relative max-w-md">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary-300" size={20} />
              <input
                type="text"
                placeholder="Search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-12 pr-4 py-3 rounded bg-white/10 border border-white/20 text-white placeholder:text-secondary-300 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-12">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {categories
            .filter((c) => CATEGORY_MAP[c.nombre])
            .map((cat) => (
              <Link
                key={cat.id}
                to={`/categoria/${cat.nombre}`}
                className="card flex flex-col items-center justify-center gap-2 py-6 hover:border-primary hover:shadow-sm transition-all group"
              >
                <div className="text-secondary-300 group-hover:text-primary transition-colors">
                  {CATEGORY_MAP[cat.nombre]?.icon || <Cpu size={24} />}
                </div>
                <span className="text-xs font-medium text-on-surface">
                  {CATEGORY_MAP[cat.nombre]?.label || cat.nombre}
                </span>
              </Link>
            ))}
        </div>
      </section>

      {/* Promotions */}
      <section className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Promociones Destacadas</h2>
          <Link to="/categoria?deals=true" className="text-sm text-primary flex items-center gap-1 hover:underline">
            View All Deals <ChevronRight size={16} />
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {PROMOS.map((promo, i) => {
            const finalPrice = Math.round(promo.original * (1 - promo.discount))
            const discountPct = Math.round(promo.discount * 100)
            return (
              <Link
                key={i}
                to={`/producto/${promo.sku}`}
                className="card hover:border-primary transition-all group"
              >
                <div className="bg-secondary-50 rounded-lg h-32 flex items-center justify-center mb-3">
                  <span className="text-secondary-200 font-mono text-xs">{promo.sku}</span>
                </div>
                <div className="mb-2">
                  <span className={`chip ${promo.stock === 'In Stock' ? 'chip-instock' : 'chip-lowstock'}`}>
                    {promo.stock}
                  </span>
                </div>
                <p className="font-mono text-[10px] text-secondary-400 mb-1">{promo.name.split(' ').slice(0, 2).join(' ')}</p>
                <p className="font-semibold text-sm leading-snug mb-2 group-hover:text-primary transition-colors">
                  {promo.name}
                </p>
                <div className="flex items-baseline gap-2">
                  <span className="font-bold text-lg">${(finalPrice / 1000).toFixed(0)}.{String(finalPrice % 1000).padStart(3, '0')}</span>
                  <span className="text-xs text-secondary-400 line-through">${(promo.original / 1000).toFixed(0)}.{String(promo.original % 1000).padStart(3, '0')}</span>
                  <span className="chip-instock text-[10px] px-1.5 py-0.5">-{discountPct}% OFF</span>
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      {/* Build CTA */}
      <section className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-16">
        <div className="bg-gradient-to-r from-primary-50 to-surface-container rounded-xl p-8 lg:p-12 border border-primary-100">
          <div className="max-w-xl">
            <h2 className="text-2xl font-bold mb-3">Build Your Dream Machine</h2>
            <p className="text-on-surface-variant text-sm mb-6">
              Use our AI-guided configurator to select compatible parts and let our masters build it for you.
            </p>
            <Link to="/asistente" className="btn-primary inline-flex items-center gap-2">
              Start Building Now <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* Products Grid */}
      <section className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8 pb-16">
        <h2 className="text-xl font-semibold mb-6">Featured Products</h2>
        {loading ? (
          <div className="text-center py-12 text-secondary-400">Loading...</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {products.slice(0, 8).map((p) => (
              <ProductCard key={p.sku} product={p} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
