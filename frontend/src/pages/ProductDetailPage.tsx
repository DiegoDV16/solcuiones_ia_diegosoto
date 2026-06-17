import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Play, ShoppingCart, Heart, Cpu, Bot, Plus, Send } from 'lucide-react'
import { getProduct, formatPrice, discountedPrice, getStockLabel } from '../api/client'
import { chatSend } from '../api/client'
import type { Product, ChatMessage } from '../types'

const SPECS_MOCK: Record<string, { label: string; value: string }[]> = {
  'CPU-INTEL-I7-14700K': [
    { label: 'ARCHITECTURE', value: 'Raptor Lake Refresh' },
    { label: 'MAX TDP', value: '253W' },
    { label: 'MEMORY TYPE', value: 'DDR5/DDR4' },
    { label: 'INTEGRATED GPU', value: 'UHD Graphics 770' },
  ],
}

export default function ProductDetailPage() {
  const { sku } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [chatOpen, setChatOpen] = useState(true)
  const [chatMsg, setChatMsg] = useState('')
  const [chat, setChat] = useState<ChatMessage[]>([
    { role: 'assistant', content: "¡Hola! Veo que estás viendo este producto. ¿Quieres que revise la compatibilidad con tu armado?" },
  ])

  useEffect(() => {
    if (!sku) return
    setLoading(true)
    getProduct(sku).then((p) => {
      setProduct(p)
      setLoading(false)
    })
  }, [sku])

  if (loading) return <div className="text-center py-20 text-secondary-400">Cargando...</div>
  if (!product) return <div className="text-center py-20 text-secondary-400">Producto no encontrado</div>

  const finalPrice = discountedPrice(product.precio_lista, product.descuento_efectivo)
  const hasDiscount = product.descuento_efectivo > 0
  const stock = getStockLabel(product.total_stock)
  const specs = SPECS_MOCK[product.sku] || [
    { label: 'SKU', value: product.sku },
    { label: 'CATEGORÍA', value: product.categoria || 'N/A' },
  ]

  const handleChat = async () => {
    if (!chatMsg.trim()) return
    const msg = chatMsg.trim()
    setChatMsg('')
    setChat((prev) => [...prev, { role: 'user', content: msg }])
    try {
      const res = await chatSend(`About ${product.sku}: ${msg}`)
      setChat((prev) => [...prev, { role: 'assistant', content: res.reply }])
    } catch {
      setChat((prev) => [...prev, { role: 'assistant', content: 'Error al procesar tu solicitud.' }])
    }
  }

  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
      {/* Breadcrumb */}
      <div className="text-xs text-secondary-400 mb-6 flex items-center gap-2">
        <Link to="/" className="hover:text-primary">Inicio</Link>
        <span>/</span>
        <Link to={`/categoria/${product.categoria}`} className="hover:text-primary capitalize">
          {product.categoria}
        </Link>
        <span>/</span>
        <span className="text-on-surface">{product.sku}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
        {/* Left - Image */}
        <div>
          <div className="bg-secondary-50 rounded-xl aspect-square flex items-center justify-center mb-4 relative overflow-hidden">
            <div className="text-center">
              <Cpu size={80} className="text-secondary-200 mx-auto mb-4" />
              <span className="font-mono text-xs text-secondary-300">{product.sku}</span>
            </div>
            <button className="absolute bottom-4 left-4 bg-black/60 text-white px-4 py-2 rounded flex items-center gap-2 text-sm hover:bg-black/80 transition-colors">
              <Play size={16} fill="white" />
              VIDEO
            </button>
          </div>
        </div>

        {/* Right - Info */}
        <div>
          <p className="font-mono text-[10px] text-secondary-400 uppercase tracking-wider mb-2">
            {product.categoria || 'Componente'}
          </p>
          <h1 className="text-2xl lg:text-3xl font-bold leading-tight mb-2">{product.nombre}</h1>

          <div className="flex items-baseline gap-3 mt-4 mb-4">
            <span className="text-3xl font-bold">{formatPrice(finalPrice)}</span>
            {hasDiscount && (
              <span className="text-lg text-secondary-400 line-through">{formatPrice(product.precio_lista)}</span>
            )}
          </div>

          <div className="flex items-center gap-3 mb-6">
            <span className={stock.className}>{stock.label} ({product.total_stock} uds.)</span>
          </div>

          <div className="flex flex-wrap gap-3 mb-8">
            <button className="btn-primary flex items-center gap-2">
              <ShoppingCart size={16} />
              Comprar
            </button>
            <button className="btn-secondary flex items-center gap-2">
              <Heart size={16} />
              Agregar a Favoritos
            </button>
          </div>

          {/* Specs */}
          <div className="border-t border-outline pt-6">
            <div className="grid grid-cols-2 gap-4">
              {specs.map((spec) => (
                <div key={spec.label}>
                  <div className="font-mono text-[10px] text-secondary-400 tracking-wider mb-1">{spec.label}</div>
                  <div className="text-sm font-medium">{spec.value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Smart Bundle */}
          <div className="mt-6 bg-primary-50 rounded-lg p-4 border border-primary-100">
            <div className="flex items-center gap-2 mb-2">
              <Bot size={16} className="text-primary" />
              <span className="font-semibold text-sm">PAQUETE INTELIGENTE IA</span>
            </div>
            <p className="text-xs text-on-surface-variant mb-3">
              Compatibilidad Optimizada. Nuestro análisis sugiere que este componente funciona bien con partes compatibles.
            </p>
            <div className="flex items-center justify-between bg-white rounded px-3 py-2 border border-outline">
              <div>
                <div className="text-xs font-medium">ROG Maximus Z790 Hero</div>
                <div className="font-mono text-[10px] text-secondary-400">$549.990</div>
              </div>
              <button className="text-primary hover:bg-primary-50 p-1.5 rounded">
                <Plus size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Technical Specs full */}
      <div className="mt-12 border-t border-outline pt-8">
        <h2 className="text-lg font-semibold mb-4">Especificaciones Técnicas</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {specs.map((spec) => (
            <div key={spec.label} className="border-b border-outline pb-3">
              <div className="font-mono text-[10px] text-secondary-400 tracking-wider mb-1">{spec.label}</div>
              <div className="text-sm">{spec.value}</div>
            </div>
          ))}
          {product.descripcion && (
            <div className="md:col-span-2 border-b border-outline pb-3">
              <div className="font-mono text-[10px] text-secondary-400 tracking-wider mb-1">DESCRIPCIÓN</div>
              <div className="text-sm">{product.descripcion}</div>
            </div>
          )}
        </div>
      </div>

      {/* Chat on product page */}
      <div className="mt-8 border border-outline rounded-lg overflow-hidden">
        <div className="bg-secondary-800 text-white px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot size={16} className="text-tertiary-400" />
            <span className="text-sm font-semibold">TechAssist IA</span>
            <span className="text-[10px] text-tertiary-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-tertiary-500 rounded-full inline-block" />
              En línea
            </span>
          </div>
        </div>
        <div className="h-48 overflow-y-auto p-4 space-y-3 bg-surface">
          {chat.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                msg.role === 'user' ? 'bg-primary text-white' : 'bg-secondary-50 text-on-surface'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
        </div>
        <div className="border-t border-outline p-3 flex gap-2">
          <input
            type="text"
            value={chatMsg}
            onChange={(e) => setChatMsg(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleChat()}
            placeholder="Pregunta sobre este producto..."
            className="input text-sm flex-1"
          />
          <button onClick={handleChat} className="bg-primary text-white p-2 rounded">
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
