'use client';

import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import './contact.css';

type Category = 'bug' | 'feature' | 'other';

export default function ContactPage() {
  const { lang } = useLanguage();
  const [category, setCategory] = useState<Category>('feature');
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');

  const isHe = lang === 'he';

  const labels = {
    title:       isHe ? 'צור קשר' : 'Contact Us',
    subtitle:    isHe ? 'שלח לנו בקשה, רעיון, או דווח על באג' : 'Send us a request, idea, or report a bug',
    name:        isHe ? 'שם (אופציונלי)' : 'Name (optional)',
    message:     isHe ? 'ההודעה שלך' : 'Your message',
    send:        isHe ? 'שלח' : 'Send',
    sending:     isHe ? 'שולח...' : 'Sending...',
    sent:        isHe ? '✓ ההודעה נשלחה! תודה.' : '✓ Message sent! Thank you.',
    error:       isHe ? 'שגיאה בשליחה, נסה שוב.' : 'Something went wrong, please try again.',
    categories: {
      bug:     isHe ? '🐛 באג' : '🐛 Bug Report',
      feature: isHe ? '💡 בקשת פיצ׳ר' : '💡 Feature Request',
      other:   isHe ? '💬 אחר' : '💬 Other',
    },
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    setStatus('sending');
    try {
      const res = await fetch('https://formsubmit.co/ajax/nirtituani13@gmail.com', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ name, _subject: `SmartBet ${category}: ${name || 'Anonymous'}`, message, category }),
      });
      setStatus(res.ok ? 'sent' : 'error');
    } catch {
      setStatus('error');
    }
  };

  return (
    <main className="contact" dir={isHe ? 'rtl' : 'ltr'}>
      <div className="contact__card glass-card glass-card-blue">
        <h1 className="contact__title">{labels.title}</h1>
        <p className="contact__subtitle">{labels.subtitle}</p>

        {status === 'sent' ? (
          <p className="contact__success">{labels.sent}</p>
        ) : (
          <form className="contact__form" onSubmit={handleSubmit}>
            <div className="contact__categories">
              {(['bug', 'feature', 'other'] as Category[]).map(c => (
                <button
                  key={c}
                  type="button"
                  className={`contact__cat-btn${category === c ? ' contact__cat-btn--active' : ''}`}
                  onClick={() => setCategory(c)}
                >
                  {labels.categories[c]}
                </button>
              ))}
            </div>

            <input
              className="contact__input"
              type="text"
              placeholder={labels.name}
              value={name}
              onChange={e => setName(e.target.value)}
            />

            <textarea
              className="contact__textarea"
              placeholder={labels.message}
              value={message}
              onChange={e => setMessage(e.target.value)}
              rows={5}
              required
            />

            {status === 'error' && <p className="contact__error">{labels.error}</p>}

            <button
              className="contact__submit"
              type="submit"
              disabled={status === 'sending' || !message.trim()}
            >
              {status === 'sending' ? labels.sending : labels.send}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}
