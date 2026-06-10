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
              The ultimate tech warehouse for builders and enthusiasts since 2024.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-secondary-200">
              <li><Link to="/about" className="hover:text-white transition-colors">About Us</Link></li>
              <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
              <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-4">Support</h4>
            <ul className="space-y-2 text-sm text-secondary-200">
              <li><Link to="/support" className="hover:text-white transition-colors">Contact Support</Link></li>
              <li><Link to="/shipping" className="hover:text-white transition-colors">Shipping Info</Link></li>
              <li><Link to="/returns" className="hover:text-white transition-colors">Return Policy</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-4">Connect</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm text-secondary-200">
                <Mail size={16} />
                <span>Newsletter</span>
              </div>
              <div className="flex gap-3">
                <Twitter size={20} className="text-secondary-200 hover:text-white cursor-pointer" />
                <Instagram size={20} className="text-secondary-200 hover:text-white cursor-pointer" />
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-secondary-600 mt-8 pt-6 text-center text-sm text-secondary-300">
          <span className="flex items-center justify-center gap-2">
            <Shield size={14} />
            <BarChart3 size={14} />
            © 2024 PC Factoría. Engineered for Performance.
          </span>
        </div>
      </div>
    </footer>
  )
}
