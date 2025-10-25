import { useState, useEffect } from 'react'

interface Step {
  name: string
  label: string
  icon: string
}

const AGENT_STEPS: Step[] = [
  { name: 'planner', label: 'Planner', icon: '🎯' },
  { name: 'rewriter', label: 'Rewriter', icon: '✍️' },
  { name: 'search', label: 'Search + RRF', icon: '🔍' },
  { name: 'generation', label: 'Generation', icon: '🤖' },
  { name: 'judge', label: 'Judge', icon: '⚖️' },
]

interface AgentStepsProps {
  isProcessing: boolean
}

export default function AgentSteps({ isProcessing }: AgentStepsProps) {
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    if (!isProcessing) {
      setCurrentStep(0)
      return
    }

    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= AGENT_STEPS.length - 1) {
          clearInterval(interval)
          return prev
        }
        return prev + 1
      })
    }, 800)

    return () => clearInterval(interval)
  }, [isProcessing])

  if (!isProcessing && currentStep === 0) return null

  return (
    <div className="flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
      {AGENT_STEPS.map((step, idx) => (
        <div key={step.name} className="flex items-center">
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all duration-300 ${
              idx <= currentStep
                ? 'bg-white shadow-sm border border-blue-200'
                : 'bg-slate-50 border border-slate-200 opacity-50'
            }`}
          >
            <span className="text-lg">{step.icon}</span>
            <span className={`text-xs font-medium ${
              idx <= currentStep ? 'text-blue-900' : 'text-slate-500'
            }`}>
              {step.label}
            </span>
            {idx === currentStep && isProcessing && (
              <div className="ml-1 w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
            )}
          </div>
          {idx < AGENT_STEPS.length - 1 && (
            <svg
              className={`w-4 h-4 mx-1 transition-colors ${
                idx < currentStep ? 'text-blue-500' : 'text-slate-300'
              }`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </div>
      ))}
    </div>
  )
}
