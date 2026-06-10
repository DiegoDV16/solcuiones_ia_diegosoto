import { useState, useRef, useEffect } from 'react'
import { Bot, MemoryStick, CheckCircle, Truck, HeadphonesIcon, Send, Paperclip, Cpu, Monitor, ShoppingCart } from 'lucide-react'
import { chatSend } from '../api/client'
import type { ChatMessage } from '../types'

const QUICK_ACTIONS = [
  { icon: <Bot size={14} />, label: 'Start New Build' },
  { icon: <CheckCircle size={14} />, label: 'Check Compatibility' },
  { icon: <Monitor size={14} />, label: 'Compare GPUs' },
  { icon: <Truck size={14} />, label: 'Next Day Shipping?' },
]

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        "Welcome back to PC Factoría. I'm TechAssist. I can help you with specifications, real-time stock levels, and custom build compatibility. What are you looking for today?",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `full_${Date.now()}`)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const msg = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: msg }])
    setLoading(true)
    try {
      const res = await chatSend(msg, sessionId)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Error: Could not reach the assistant. Please try again.' },
      ])
    }
    setLoading(false)
  }

  const handleQuickAction = (label: string) => {
    setInput(label)
  }

  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left sidebar */}
        <aside className="lg:col-span-1 order-2 lg:order-1">
          <div className="card space-y-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Bot size={18} className="text-primary" />
              TechAssist AI
              <span className="chip-instock text-[10px] ml-auto">Online</span>
            </div>

            <nav className="space-y-1">
              {[
                { icon: <Bot size={14} />, label: 'Assistant' },
                { icon: <MemoryStick size={14} />, label: 'Hardware Specs' },
                { icon: <CheckCircle size={14} />, label: 'Compatibility' },
                { icon: <Truck size={14} />, label: 'Order Status' },
                { icon: <HeadphonesIcon size={14} />, label: 'Human Support' },
              ].map((item) => (
                <button
                  key={item.label}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded hover:bg-secondary-50 transition-colors text-left"
                >
                  {item.icon}
                  {item.label}
                </button>
              ))}
            </nav>

            <div className="border-t border-outline pt-4">
              <button className="btn-primary w-full text-sm" onClick={() => handleQuickAction('Start New Build')}>
                Start New Build
              </button>
            </div>

            {/* Current Config */}
            <div className="border-t border-outline pt-4">
              <h4 className="font-mono text-[10px] text-secondary-400 uppercase tracking-wider mb-2">
                Current Configuration
              </h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-on-surface-variant">RTX 4070 Dual</span>
                  <span className="font-mono">$599.00</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-on-surface-variant">i7-13700K</span>
                  <span className="font-mono">$385.50</span>
                </div>
                <div className="border-t border-outline pt-2 flex items-center justify-between text-sm font-semibold">
                  <span>Total</span>
                  <span className="font-mono">$984.50</span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Chat area */}
        <div className="lg:col-span-3 order-1 lg:order-2">
          {/* Terminal header */}
          <div className="bg-secondary-800 text-white rounded-t-lg px-4 py-3 flex items-center gap-2">
            <div className="flex gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
              <span className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
              <span className="w-2.5 h-2.5 rounded-full bg-green-500" />
            </div>
            <span className="font-mono text-xs text-secondary-200 ml-2">
              Support Terminal v2.4 — Hardware Intelligence Engine
            </span>
            <span className="ml-auto chip-instock text-[10px]">SYSTEM READY</span>
          </div>

          {/* Messages */}
          <div className="h-[500px] overflow-y-auto p-4 space-y-4 bg-surface border-x border-outline">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className="flex gap-2 max-w-[80%]">
                  {msg.role === 'assistant' && (
                    <div className="shrink-0 mt-1">
                      <Bot size={18} className="text-primary" />
                    </div>
                  )}
                  <div
                    className={`rounded-lg px-4 py-2.5 text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-primary text-white'
                        : 'bg-secondary-50 text-on-surface'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="flex gap-2">
                  <Bot size={18} className="text-primary" />
                  <div className="bg-secondary-50 rounded-lg px-4 py-2.5 text-sm text-secondary-400">
                    <span className="animate-pulse">Processing your request...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border border-outline rounded-b-lg p-3 bg-surface-container-lowest">
            {/* Quick actions */}
            <div className="flex flex-wrap gap-2 mb-3">
              {QUICK_ACTIONS.map((action) => (
                <button
                  key={action.label}
                  onClick={() => handleQuickAction(action.label)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded border border-outline hover:bg-secondary-50 transition-colors"
                >
                  {action.icon}
                  {action.label}
                </button>
              ))}
            </div>

            <div className="flex gap-2">
              <button className="p-2 text-secondary-400 hover:text-on-surface">
                <Paperclip size={18} />
              </button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your message here..."
                className="input text-sm flex-1"
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="bg-primary text-white p-2.5 rounded disabled:opacity-50 hover:bg-primary-600 transition-colors"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
