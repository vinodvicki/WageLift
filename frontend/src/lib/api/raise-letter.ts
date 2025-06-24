/**
 * Raise Letter API Module
 * Mock implementation for development
 */

export type LetterTone = 'professional' | 'confident' | 'collaborative' | 'assertive'
export type LetterLength = 'concise' | 'standard' | 'detailed'

export interface RaiseLetterData {
  currentSalary: number
  requestedSalary: number
  marketData?: {
    medianSalary: number
    percentile: number
  }
  achievements: string[]
  tone: LetterTone
  length: LetterLength
  customPoints?: string[]
}

export interface GeneratedLetter {
  id: string
  content: string
  subject: string
  createdAt: string
  data: RaiseLetterData
}

/**
 * Mock hook for raise letter API
 */
export function useRaiseLetterAPI() {
  const generateLetter = async (data: RaiseLetterData): Promise<GeneratedLetter> => {
    // Mock delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    return {
      id: `letter_${Date.now()}`,
      content: `Dear [Manager Name],

I hope this message finds you well. I am writing to discuss my compensation and request a salary adjustment.

Based on my research and current market conditions, I believe my contributions warrant a salary increase from $${data.currentSalary.toLocaleString()} to $${data.requestedSalary.toLocaleString()}.

Key achievements:
${data.achievements.map(achievement => `• ${achievement}`).join('\n')}

I would welcome the opportunity to discuss this further at your convenience.

Best regards,
[Your Name]`,
      subject: 'Request for Salary Review',
      createdAt: new Date().toISOString(),
      data
    }
  }

  const saveLetter = async (letter: GeneratedLetter): Promise<void> => {
    // Mock save
    console.log('Letter saved:', letter.id)
  }

  const getLetterHistory = async (): Promise<GeneratedLetter[]> => {
    // Mock history
    return []
  }

  return {
    generateLetter,
    saveLetter,
    getLetterHistory,
    isLoading: false,
    error: null
  }
}