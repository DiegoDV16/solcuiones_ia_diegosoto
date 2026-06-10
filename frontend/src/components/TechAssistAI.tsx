import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, X, Send } from 'lucide-react'
import { chatSend } from '../api/client'
import type { ChatMessage } from '../types'

export default function TechAssistAI() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        "Hi! Need help building your PC? I can suggest the best components for your budget and use case.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `web_${Date.now()}`)
  const bottomRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    try {
      const res = await chatSend(userMsg, sessionId)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ])
    }
    setLoading(false)
  }

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-50 bg-secondary-800 text-white p-3.5 rounded-full shadow-lg hover:bg-secondary-700 transition-all hover:scale-105"
        >
          <Bot size={20} />
        </button>
      )}

      {open && (
        <div className="fixed bottom-6 right-6 z-50 w-80 sm:w-96 shadow-2xl rounded-xl overflow-hidden border border-outline bg-surface-container-lowest">
          <div className="bg-secondary-800 text-white px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot size={18} className="text-tertiary-400" />
              <div>
                <div className="text-sm font-semibold">TechAssist AI</div>
                <div className="flex items-center gap-1 text-[10px] text-tertiary-400">
                  <span className="w-1.5 h-1.5 bg-tertiary-500 rounded-full inline-block" />
                  Status: Online
                </div>
              </div>
            </div>
            <button onClick={() => setOpen(false)} className="text-secondary-200 hover:text-white p-1">
              <X size={16} />
            </button>
          </div>

          <div
            className="h-80 overflow-y-auto p-4 space-y-3 bg-surface"
            onClick={() => navigate('/asistente')}
          >
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] rounded-lg px-3 py-2 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-primary text-white'
                      : 'bg-secondary-50 text-on-surface'
                  }`}
                >
                  {msg.content.split('\n').map((line, j) => (
                    <span key={j}>
                      {line}
                      {j < msg.content.split('\n').length - 1 && <br />}
                    </span>
                  ))}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-secondary-50 rounded-lg px-3 py-2 text-sm text-secondary-400">
                  Thinking...
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="border-t border-outline p-3 bg-surface-container-lowest">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask about components..."
                className="input text-sm flex-1"
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="bg-primary text-white p-2 rounded disabled:opacity-50 hover:bg-primary-600 transition-colors"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
