import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import Home from '../app/page'

describe('Home Page', () => {
  it('renders without crashing', () => {
    render(<Home />)
    expect(screen.getByRole('main')).toBeInTheDocument()
  })

  it('contains WageLift branding', () => {
    render(<Home />)
    expect(screen.getByText(/WageLift/i)).toBeInTheDocument()
  })

  it('has proper heading structure', () => {
    render(<Home />)
    const headings = screen.getAllByRole('heading')
    expect(headings.length).toBeGreaterThan(0)
  })
}) 