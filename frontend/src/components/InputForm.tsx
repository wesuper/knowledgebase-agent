import React, { useState } from 'react';

interface InputFormProps {
  onSubmit: (inputText: string) => void;
  isLoading: boolean;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit, isLoading }) => {
  const [inputText, setInputText] = useState<string>('');

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!inputText.trim()) {
      alert('Please enter some text.'); // Basic validation
      return;
    }
    onSubmit(inputText);
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
      <textarea
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="Enter text with URLs here (e.g., Check out https://www.google.com and https://www.wikipedia.org)"
        rows={6} // Slightly more rows
        disabled={isLoading}
        // Using global styles for textarea, so specific styles here can be minimal
        style={{ width: '100%', resize: 'vertical' }}
      />
      <button
        type="submit"
        disabled={isLoading}
        // Using global styles for button
        style={{ padding: '12px 20px', fontSize: '1.1em' }} // Make button a bit larger
      >
        {isLoading ? 'Processing...' : 'Submit URLs'}
      </button>
    </form>
  );
};

export default InputForm;
