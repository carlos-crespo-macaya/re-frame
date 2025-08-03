import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LanguageSelector } from '../LanguageSelector';

describe('LanguageSelector', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('renders correctly with default value', () => {
    render(<LanguageSelector value="en-US" onChange={mockOnChange} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('handles language change', async () => {
    render(<LanguageSelector value="en-US" onChange={mockOnChange} />);
    
    const select = screen.getByRole('combobox');
    await userEvent.selectOptions(select, 'es-ES');
    
    expect(mockOnChange).toHaveBeenCalledWith('es-ES');
  });

  it('language selector should display "Language" as label', () => {
    const { getByText, queryByText } = render(
      <LanguageSelector value="en-US" onChange={mockOnChange} />
    );
    
    expect(getByText('Language')).toBeInTheDocument();
    expect(queryByText('Select Language')).not.toBeInTheDocument();
  });

  it('language selector should display simplified label in Spanish', () => {
    const { getByText, queryByText } = render(
      <LanguageSelector value="es-ES" onChange={mockOnChange} />
    );
    
    expect(getByText('Idioma')).toBeInTheDocument();
    expect(queryByText('Seleccionar idioma')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <LanguageSelector value="en-US" onChange={mockOnChange} className="custom-class" />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('has compact sizing for mobile', () => {
    render(<LanguageSelector value="en-US" onChange={mockOnChange} />);
    
    const select = screen.getByRole('combobox');
    expect(select).toHaveClass('px-2', 'py-1', 'text-sm');
  });
});