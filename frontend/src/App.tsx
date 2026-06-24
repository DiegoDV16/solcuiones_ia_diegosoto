import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import TechAssistAI from './components/TechAssistAI'
import HomePage from './pages/HomePage'
import CategoryPage from './pages/CategoryPage'
import ProductDetailPage from './pages/ProductDetailPage'
import AIAssistantPage from './pages/AIAssistantPage'
import AccountPage from './pages/AccountPage'
import CartPage from './pages/CartPage'
import OrderTrackingPage from './pages/OrderTrackingPage'
import RecommendationsPage from './pages/RecommendationsPage'
import AboutPage from './pages/AboutPage'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/categoria/:category" element={<CategoryPage />} />
          <Route path="/categoria" element={<CategoryPage />} />
          <Route path="/producto/:sku" element={<ProductDetailPage />} />
          <Route path="/asistente" element={<AIAssistantPage />} />
          <Route path="/carrito" element={<CartPage />} />
          <Route path="/ordenes" element={<OrderTrackingPage />} />
          <Route path="/recomendaciones" element={<RecommendationsPage />} />
          <Route path="/nosotros" element={<AboutPage />} />
          <Route path="/cuenta" element={<AccountPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
      <TechAssistAI />
    </div>
  )
}
