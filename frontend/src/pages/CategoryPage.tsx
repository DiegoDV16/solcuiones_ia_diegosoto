import { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight, SlidersHorizontal } from 'lucide-react'
import ProductCard from '../components/ProductCard'
import { getProducts, getCategories } from '../api/client'
import type { Product, Category } from '../types'

export default function CategoryPage() {
  const { category } = useParams()
  const [searchParams] = useSearchParams()
  const searchQuery = searchParams.get('search') || ''
  const dealsOnly = searchParams.get('deals') === 'true'

  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCat, setSelectedCat] = useState(category || '')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setSelectedCat(category || '')
  }, [category])

  useEffect(() => {
    setLoading(true)
    const params: { category?: string; search?: string } = {}
    if (selectedCat) params.category = selectedCat
    if (searchQuery) params.search = searchQuery
    Promise.all([getProducts(params), getCategories()]).then(([prods, cats]) => {
      let filtered = prods
      if (dealsOnly) {
        filtered = filtered.filter((p) => p.descuento_efectivo > 0)
      }
      setProducts(filtered)
      setCategories(cats)
      setLoading(false)
    })
  }, [selectedCat, searchQuery, dealsOnly])

  const title = dealsOnly
    ? 'Ofertas'
    : selectedCat
    ? categories.find((c) => c.nombre === selectedCat)?.nombre || selectedCat
    : searchQuery
    ? `Búsqueda: "${searchQuery}"`
    : 'Todos los Productos'

  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
      <h1 className="text-2xl font-bold mb-6 capitalize">{title}</h1>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filters sidebar */}
        <aside className="w-full lg:w-56 shrink-0">
          <div className="flex items-center justify-between lg:mb-4 mb-2">
            <h3 className="font-semibold text-sm flex items-center gap-2">
              <SlidersHorizontal size={14} />
              Filtros
            </h3>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-2">
                Categoría
              </h4>
              <div className="flex flex-wrap lg:flex-col gap-1.5">
                <button
                  onClick={() => setSelectedCat('')}
                  className={`text-xs px-3 py-1.5 rounded transition-colors text-left ${
                    !selectedCat && !dealsOnly
                      ? 'bg-primary text-white'
                      : 'bg-secondary-50 hover:bg-secondary-100 text-on-surface'
                  }`}
                >
                  Todas
                </button>
                {categories.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedCat(c.nombre)}
                    className={`text-xs px-3 py-1.5 rounded transition-colors text-left capitalize ${
                      selectedCat === c.nombre
                        ? 'bg-primary text-white'
                        : 'bg-secondary-50 hover:bg-secondary-100 text-on-surface'
                    }`}
                  >
                    {c.nombre}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* Products */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-on-surface-variant">
              Mostrando {products.length} resultados
            </span>
            <select className="text-xs border border-outline rounded px-2 py-1.5 bg-surface-container-lowest">
              <option>Ordenar por</option>
              <option>Precio: Menor a Mayor</option>
              <option>Precio: Mayor a Menor</option>
              <option>Más Recientes</option>
              <option>Más Vendidos</option>
            </select>
          </div>

          {loading ? (
            <div className="text-center py-16 text-secondary-400">Cargando...</div>
          ) : products.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-secondary-400 mb-2">No se encontraron productos</p>
              <p className="text-xs text-secondary-300">Prueba ajustando los filtros o términos de búsqueda</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {products.map((p) => (
                <ProductCard key={p.sku} product={p} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {products.length > 0 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button className="p-2 rounded border border-outline hover:bg-secondary-50">
                <ChevronLeft size={16} />
              </button>
              <button className="px-3 py-1.5 rounded bg-primary text-white text-sm">1</button>
              <button className="px-3 py-1.5 rounded border border-outline text-sm hover:bg-secondary-50">2</button>
              <button className="px-3 py-1.5 rounded border border-outline text-sm hover:bg-secondary-50">3</button>
              <span className="px-2 text-secondary-400 text-sm">...</span>
              <button className="px-3 py-1.5 rounded border border-outline text-sm hover:bg-secondary-50">12</button>
              <button className="p-2 rounded border border-outline hover:bg-secondary-50">
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
