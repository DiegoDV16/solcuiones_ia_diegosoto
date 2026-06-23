import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ShoppingCart, Check } from 'lucide-react'
import type { Product } from '../types'
import { formatPrice, discountedPrice, getStockLabel } from '../api/client'
import { useCart } from '../context/CartContext'

interface Props {
  product: Product
}

export default function ProductCard({ product }: Props) {
  const cart = useCart()
  const stock = getStockLabel(product.total_stock)
  const hasDiscount = product.descuento_efectivo > 0
  const finalPrice = discountedPrice(product.precio_lista, product.descuento_efectivo)
  const categorySlug = product.categoria?.toLowerCase() || ''
  const [added, setAdded] = useState(false)

  const handleAdd = () => {
    cart.add(product.sku, product.nombre, finalPrice)
    setAdded(true)
    setTimeout(() => setAdded(false), 2000)
  }

  return (
    <div className="card group hover:border-primary transition-colors duration-200 flex flex-col">
      <div className="bg-secondary-50 rounded-lg h-40 flex items-center justify-center mb-4 overflow-hidden">
        <div className="text-secondary-200 font-mono text-xs text-center px-2">
          <div className="text-3xl mb-1 opacity-30">
            {categorySlug === 'video' ? '🎮' : categorySlug === 'procesadores' ? '⚡' : '🔧'}
          </div>
          <span className="font-mono text-[10px]">{product.sku}</span>
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <span className="font-mono text-[10px] text-secondary-400 uppercase tracking-wider mb-1">
          {product.categoria || 'Componente'}
        </span>

        <Link to={`/producto/${product.sku}`} className="block">
          <h3 className="font-semibold text-sm leading-snug mb-2 group-hover:text-primary transition-colors">
            {product.nombre}
          </h3>
        </Link>

        <div className="mb-3">
          <span className={stock.className}>{stock.label}</span>
        </div>

        <div className="mt-auto">
          <div className="flex items-baseline gap-2 mb-3">
            <span className="font-bold text-lg">{formatPrice(finalPrice)}</span>
            {hasDiscount && (
              <span className="text-xs text-secondary-400 line-through">
                {formatPrice(product.precio_lista)}
              </span>
            )}
            {hasDiscount && (
              <span className="chip-instock text-[10px] px-1.5 py-0.5">
                -{Math.round(product.descuento_efectivo * 100)}%
              </span>
            )}
          </div>

          <button
            onClick={handleAdd}
            className={`btn-primary w-full flex items-center justify-center gap-2 text-xs ${
              added ? 'bg-tertiary-600' : ''
            }`}
          >
            {added ? <Check size={14} /> : <ShoppingCart size={14} />}
            {added ? 'Agregado' : 'Agregar al Carrito'}
          </button>
        </div>
      </div>
    </div>
  )
}
