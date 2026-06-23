import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Cpu, Shield, Users, Award, MapPin, HeadphonesIcon } from 'lucide-react'
import { getBranches } from '../api/client'
import type { Branch } from '../types'

const values = [
  { icon: <Cpu size={24} />, title: 'Tecnología de Punta', desc: 'Los componentes más avanzados del mercado global.' },
  { icon: <Shield size={24} />, title: 'Calidad Garantizada', desc: 'Todos nuestros productos pasan por rigurosos controles.' },
  { icon: <Users size={24} />, title: 'Equipo Experto', desc: 'Más de 10 años asesorando a la comunidad tech en Chile.' },
  { icon: <Award size={24} />, title: 'Precios Justos', desc: 'Los mejores precios del mercado con descuentos exclusivos.' },
]

export default function AboutPage() {
  const [branches, setBranches] = useState<Branch[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getBranches()
      .then(setBranches)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
      {/* Hero */}
      <section className="text-center py-12 lg:py-16">
        <Cpu size={48} className="mx-auto text-primary mb-4" />
        <h1 className="text-3xl lg:text-4xl font-bold mb-4">PC Factoría</h1>
        <p className="text-secondary-400 max-w-2xl mx-auto">
          Desde 2024, somos la tienda líder en componentes de computación en Chile. 
          Nacimos de la pasión por la tecnología y el gaming, y hoy ayudamos a miles 
          de chilenos a construir la PC de sus sueños.
        </p>
      </section>

      {/* Valores */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {values.map((v) => (
          <div key={v.title} className="card p-6 text-center hover:border-primary transition-colors">
            <div className="text-primary mb-3 flex justify-center">{v.icon}</div>
            <h3 className="font-semibold text-sm mb-2">{v.title}</h3>
            <p className="text-xs text-secondary-400">{v.desc}</p>
          </div>
        ))}
      </section>

      {/* Stats */}
      <section className="bg-gradient-to-r from-primary-50 to-surface-container rounded-xl p-8 mb-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            { num: '10K+', label: 'Clientes Satisfechos' },
            { num: '500+', label: 'Productos en Stock' },
            { num: `${branches.length}+`, label: 'Sucursales en Chile' },
            { num: '4.9', label: 'Calificación Promedio' },
          ].map((s) => (
            <div key={s.label}>
              <div className="text-2xl font-bold text-primary">{s.num}</div>
              <div className="text-xs text-secondary-400">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Mapa sucursales */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
          <MapPin size={20} className="text-primary" /> Nuestras Sucursales
        </h2>
        <div className="card p-6">
          {loading ? (
            <div className="animate-pulse space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-4 bg-secondary-100 rounded w-2/3" />
              ))}
            </div>
          ) : (
            <>
              <p className="text-sm text-secondary-400 mb-4">
                Contamos con {branches.length} sucursales en Chile. Visítanos para recibir asesoría personalizada.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                {branches.map((b) => (
                  <div key={b.codigo} className="flex items-center gap-2 text-secondary-400">
                    <MapPin size={14} className="text-primary shrink-0" />
                    <span>{b.nombre} - {b.comuna}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </section>

      {/* Contacto */}
      <section className="text-center">
        <h2 className="text-xl font-semibold mb-4 flex items-center justify-center gap-2">
          <HeadphonesIcon size={20} className="text-primary" /> ¿Hablamos?
        </h2>
        <p className="text-secondary-400 text-sm mb-6">
          ¿Tienes dudas? Nuestro equipo está listo para ayudarte.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link to="/asistente" className="btn-primary">
            Asistente IA
          </Link>
          <a href="mailto:soporte@pcfactoria.cl" className="btn-secondary">
            soporte@pcfactoria.cl
          </a>
        </div>
      </section>
    </div>
  )
}
