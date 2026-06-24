import { Link } from 'react-router-dom'
import { Package, Heart, HeadphonesIcon, ShoppingCart, Cpu } from 'lucide-react'

const LINKS = [
  {
    icon: <Package size={20} />,
    label: 'Mis Órdenes',
    desc: 'Revisa el estado de tus compras y su seguimiento',
    to: '/ordenes',
  },
  {
    icon: <Heart size={20} />,
    label: 'Favoritos',
    desc: 'Tus productos guardados para armados futuros',
    to: '/categoria?favorites=true',
  },
  {
    icon: <ShoppingCart size={20} />,
    label: 'Carrito',
    desc: 'Productos listos para comprar',
    to: '/carrito',
  },
  {
    icon: <HeadphonesIcon size={20} />,
    label: 'Soporte Técnico',
    desc: 'Asistente IA para compatibilidad y recomendaciones',
    to: '/asistente',
  },
]

export default function AccountPage() {
  const favorites: string[] = JSON.parse(localStorage.getItem('favorites') || '[]')

  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
      <div className="flex items-center gap-3 mb-8">
        <Cpu size={32} className="text-primary" />
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Mi Cuenta</h1>
          <p className="text-sm text-secondary-400">PC Factoría Chile</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {LINKS.map((link) => (
          <Link
            key={link.label}
            to={link.to}
            className="card flex items-start gap-4 p-5 hover:shadow-md transition-shadow"
          >
            <div className="text-primary mt-0.5">{link.icon}</div>
            <div>
              <h3 className="font-semibold text-on-surface">{link.label}</h3>
              <p className="text-sm text-secondary-400">{link.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      <div className="card p-5">
        <h2 className="font-semibold text-on-surface mb-3">Favoritos</h2>
        {favorites.length > 0 ? (
          <div className="space-y-2">
            {favorites.map((sku) => (
              <Link
                key={sku}
                to={`/producto/${encodeURIComponent(sku)}`}
                className="block text-sm text-primary hover:underline"
              >
                {sku}
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-sm text-secondary-400">
            No tienes productos favoritos aún. Navega por el catálogo y guarda tus preferidos.
          </p>
        )}
      </div>
    </div>
  )
}