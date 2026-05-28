import React from 'react';
import styles from './Header.module.css';

interface HeaderProps {
  onReset?: () => void;
  showReset?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onReset, showReset }) => {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <div className={styles.brand} onClick={showReset ? onReset : undefined} style={{ cursor: showReset ? 'pointer' : 'default' }}>
          <div className={styles.logoMark}>
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <path d="M14 2L26 8V20L14 26L2 20V8L14 2Z" stroke="currentColor" strokeWidth="1.5" fill="none"/>
              <path d="M14 7V14.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="14" cy="19" r="1.5" fill="currentColor"/>
            </svg>
          </div>
          <div className={styles.brandText}>
            <span className={styles.brandName}>RedFlag</span>
            <span className={styles.brandTagline}>Legal Clarity Engine</span>
          </div>
        </div>

        <nav className={styles.nav}>
          <span className={styles.badge}>
            <span className={styles.badgeDot} />
            Karnataka Rent Act 2025/26
          </span>
          {showReset && (
            <button className={styles.resetBtn} onClick={onReset}>
              ← New Analysis
            </button>
          )}
        </nav>
      </div>
    </header>
  );
};
