import { Link } from 'react-router-dom'
import { Cpu, Shield, BarChart3, Mail, Twitter, Instagram } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-secondary-800 text-white mt-auto">
      <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 text-primary font-bold text-lg mb-4">
              <Cpu size={24} />
              <span>PC Factoría</span>
            </div>
            <p className="text-secondary-200 text-sm leading-relaxed">
              El mejor almacén tecnológico para constructores y entusiastas desde 2024.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-4">Empresa</h4>
            <ul className="space-y-2 text-sm text-secondary-200">
              <li><Link to="/nosotros" className="hover:text-white transition-colors">Nosotros</Link></li>
              <li><Link to="/recomendaciones" className="hover:text-white transition-colors">Recomendaciones IA</Link></li>
              <li><Link to="/ordenes" className="hover:text-white transition-colors">Seguimiento de Órdenes</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-4">Soporte</h4>
            <ul className="space-y-2 text-sm text-secondary-200">
              <li><Link to="/asistente" className="hover:text-white transition-colors">Asistente IA</Link></li>
              <li><Link to="/carrito" className="hover:text-white transition-colors">Carrito de Compras</Link></li>
              <li><Link to="/categoria" className="hover:text-white transition-colors">Productos</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-4">Conectar</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm text-secondary-200">
                <Mail size={16} />
                <span>Newsletter</span>
              </div>
              <div className="flex gap-3">
                <a href="https://twitter.com/pcfactoria" target="_blank" rel="noopener noreferrer">
                  <Twitter size={20} className="text-secondary-200 hover:text-white cursor-pointer" />
                </a>
                <a href="https://instagram.com/pcfactoria" target="_blank" rel="noopener noreferrer">
                  <Instagram size={20} className="text-secondary-200 hover:text-white cursor-pointer" />
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-secondary-600 mt-8 pt-6 text-center text-sm text-secondary-300">
          <span className="flex items-center justify-center gap-2">
            <Shield size={14} />
            <BarChart3 size={14} />
            © 2024 PC Factoría. Diseñado para el Rendimiento.
          </span>
        </div>
      </div>
    </footer>
  )
}
