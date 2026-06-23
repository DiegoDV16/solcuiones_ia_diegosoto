import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, ShoppingCart, User, Menu, X, Cpu } from 'lucide-react'
import { useCart } from '../context/CartContext'

const CATEGORIES = [
  { name: 'Ofertas', path: '/categoria?deals=true' },
  { name: 'Recomendaciones', path: '/recomendaciones' },
  { name: 'Órdenes', path: '/ordenes' },
  { name: 'Soporte', path: '/asistente' },
]

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()
  const { count } = useCart()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/categoria?search=${encodeURIComponent(searchQuery.trim())}`)
      setSearchQuery('')
      setSearchOpen(false)
    }
  }

  return (
    <header className="sticky top-0 z-50 bg-surface-container-lowest border-b border-outline">
      <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 text-primary font-bold text-xl">
            <Cpu size={28} />
            <span>PC Factoría</span>
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            {CATEGORIES.map((cat) => (
              <Link
                key={cat.name}
                to={cat.path}
                className="text-sm font-medium text-on-surface hover:text-primary transition-colors"
              >
                {cat.name}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setSearchOpen(!searchOpen)}
              className="p-2 text-secondary-400 hover:text-on-surface transition-colors"
            >
              <Search size={20} />
            </button>
            <button
              onClick={() => navigate('/carrito')}
              className="p-2 text-secondary-400 hover:text-on-surface transition-colors hidden sm:block relative"
            >
              <ShoppingCart size={20} />
              {count > 0 && (
                <span className="absolute -top-0.5 -right-0.5 bg-primary text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                  {count > 9 ? '9+' : count}
                </span>
              )}
            </button>
            <button className="p-2 text-secondary-400 hover:text-on-surface transition-colors hidden sm:block">
              <User size={20} />
            </button>
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden p-2 text-secondary-400 hover:text-on-surface"
            >
              {menuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {searchOpen && (
          <form onSubmit={handleSearch} className="pb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-300" size={18} />
              <input
                type="text"
                placeholder="Buscar productos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10"
                autoFocus
              />
            </div>
          </form>
        )}

        {menuOpen && (
          <div className="pb-4 md:hidden border-t border-outline pt-4">
            <nav className="flex flex-col gap-3">
              {CATEGORIES.map((cat) => (
                <Link
                  key={cat.name}
                  to={cat.path}
                  onClick={() => setMenuOpen(false)}
                  className="text-sm font-medium text-on-surface hover:text-primary py-1"
                >
                  {cat.name}
                </Link>
              ))}
              <div className="flex gap-4 pt-2 border-t border-outline">
                <Link to="/carrito" className="text-sm flex items-center gap-1">
                  <ShoppingCart size={16} /> Carrito
                </Link>
                <Link to="/cuenta" className="text-sm flex items-center gap-1">
                  <User size={16} /> Cuenta
                </Link>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
