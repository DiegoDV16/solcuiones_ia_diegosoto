import { useEffect, useMemo, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight, SlidersHorizontal } from 'lucide-react'
import ProductCard from '../components/ProductCard'
import { SkeletonCard } from '../components/Skeleton'
import { getProducts, getCategories } from '../api/client'
import type { Product, Category } from '../types'

const PAGE_SIZE = 9

export default function CategoryPage() {
  const { category } = useParams()
  const [searchParams] = useSearchParams()
  const searchQuery = searchParams.get('search') || ''
  const dealsOnly = searchParams.get('deals') === 'true'

  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCat, setSelectedCat] = useState(category || '')
  const [loading, setLoading] = useState(true)
  const [sort, setSort] = useState('')
  const [page, setPage] = useState(1)

  useEffect(() => {
    setSelectedCat(category || '')
    setPage(1)
  }, [category])

  useEffect(() => {
    setPage(1)
  }, [sort, selectedCat, searchQuery, dealsOnly])

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

  const sorted = useMemo(() => {
    const list = [...products]
    if (sort === 'price-asc') list.sort((a, b) => a.precio_lista - b.precio_lista)
    else if (sort === 'price-desc') list.sort((a, b) => b.precio_lista - a.precio_lista)
    else if (sort === 'name') list.sort((a, b) => a.nombre.localeCompare(b.nombre))
    return list
  }, [products, sort])

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)
  const paginated = sorted.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)

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
                  onClick={() => { setSelectedCat(''); setPage(1) }}
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
                    onClick={() => { setSelectedCat(c.nombre); setPage(1) }}
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
              Mostrando {sorted.length} resultados
            </span>
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="text-xs border border-outline rounded px-2 py-1.5 bg-surface-container-lowest"
            >
              <option value="">Ordenar por</option>
              <option value="price-asc">Precio: Menor a Mayor</option>
              <option value="price-desc">Precio: Mayor a Menor</option>
              <option value="name">Nombre A-Z</option>
            </select>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : paginated.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-secondary-400 mb-2">No se encontraron productos</p>
              <p className="text-xs text-secondary-300">Prueba ajustando los filtros o términos de búsqueda</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {paginated.map((p) => (
                <ProductCard key={p.sku} product={p} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="p-2 rounded border border-outline hover:bg-secondary-50 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={16} />
              </button>
              {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                let pageNum: number
                if (totalPages <= 7) {
                  pageNum = i + 1
                } else if (currentPage <= 4) {
                  pageNum = i + 1
                } else if (currentPage >= totalPages - 3) {
                  pageNum = totalPages - 6 + i
                } else {
                  pageNum = currentPage - 3 + i
                }
                return (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={`px-3 py-1.5 rounded text-sm ${
                      currentPage === pageNum
                        ? 'bg-primary text-white'
                        : 'border border-outline hover:bg-secondary-50'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}
              <button
                onClick={() => setPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="p-2 rounded border border-outline hover:bg-secondary-50 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
