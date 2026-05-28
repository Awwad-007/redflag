import React from 'react';
import styles from './HeroSection.module.css';

const features = [
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M4 16V6l6-4 6 4v10H4Z" stroke="currentColor" strokeWidth="1.5" fill="none"/>
        <path d="M8 16v-5h4v5" stroke="currentColor" strokeWidth="1.5"/>
      </svg>
    ),
    title: 'Rent Deposit Check',
    desc: 'Flags any security deposit exceeding the 2-month cap under Karnataka law',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <rect x="3" y="3" width="14" height="14" rx="2" stroke="currentColor" strokeWidth="1.5"/>
        <path d="M7 7h6M7 10h4M7 13h3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    ),
    title: 'Clause-by-Clause Analysis',
    desc: 'Every flagged term is mapped to the exact statutory rule it violates',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/>
        <path d="M10 6v4l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    ),
    title: 'Notice Period Validator',
    desc: 'Checks rent revision and eviction clauses against mandatory notice periods',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 2L2 7v6l8 5 8-5V7L10 2Z" stroke="currentColor" strokeWidth="1.5" fill="none"/>
        <path d="M10 7v4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        <circle cx="10" cy="13" r="1" fill="currentColor"/>
      </svg>
    ),
    title: 'Illegal Clause Detection',
    desc: 'Utility cutoff threats, illegal entry clauses, and predatory penalty terms',
  },
];

export const HeroSection: React.FC = () => {
  return (
    <section className={styles.hero}>
      <div className={styles.eyebrow}>
        <span className={styles.eyebrowText}>AI-Powered · Karnataka Rent Act 2025/26</span>
      </div>

      <h1 className={styles.headline}>
        Your rental contract,
        <br />
        <em>legally decoded.</em>
      </h1>

      <p className={styles.subline}>
        Upload any rental agreement. RedFlag instantly identifies illegal clauses,
        predatory terms, and statutory violations — in plain language.
      </p>

      <div className={styles.featureGrid}>
        {features.map((f, i) => (
          <div key={i} className={styles.featureCard} style={{ animationDelay: `${i * 80}ms` }}>
            <div className={styles.featureIcon}>{f.icon}</div>
            <div>
              <p className={styles.featureTitle}>{f.title}</p>
              <p className={styles.featureDesc}>{f.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
