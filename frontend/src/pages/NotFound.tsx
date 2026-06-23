import { Link } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-20 text-center">
      <div className="text-8xl font-bold text-secondary-100 mb-4">404</div>
      <h1 className="text-2xl font-bold mb-2">Página no encontrada</h1>
      <p className="text-secondary-400 mb-8 max-w-md mx-auto">
        La página que buscas no existe o ha sido movida.
      </p>
      <div className="flex justify-center gap-4">
        <Link to="/" className="btn-primary inline-flex items-center gap-2">
          <Home size={16} /> Ir al Inicio
        </Link>
        <button onClick={() => window.history.back()} className="btn-secondary inline-flex items-center gap-2">
          <ArrowLeft size={16} /> Volver
        </button>
      </div>
    </div>
  )
}
