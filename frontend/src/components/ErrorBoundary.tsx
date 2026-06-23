import { Component, type ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (!this.state.hasError) return this.props.children
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center px-4">
        <AlertTriangle size={48} className="text-red-400 mb-4" />
        <h2 className="text-xl font-bold mb-2">Algo salió mal</h2>
        <p className="text-secondary-400 text-sm mb-6 max-w-md">
          {this.state.error?.message || 'Ocurrió un error inesperado.'}
        </p>
        <button
          onClick={() => { this.setState({ hasError: false }); window.location.reload() }}
          className="btn-primary inline-flex items-center gap-2"
        >
          <RefreshCw size={16} /> Reintentar
        </button>
      </div>
    )
  }
}
