import React, { useState } from 'react';
import styles from './FlagCard.module.css';
import type { Flag, Severity } from '../types';

interface FlagCardProps {
  flag: Flag;
  index: number;
}

const severityConfig: Record<Severity, { label: string; className: string; icon: React.ReactNode }> = {
  CRITICAL: {
    label: 'Critical Violation',
    className: styles.critical,
    icon: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M7 1L13 12H1L7 1Z" stroke="currentColor" strokeWidth="1.5" fill="none"/>
        <path d="M7 5.5v3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        <circle cx="7" cy="10" r="0.75" fill="currentColor"/>
      </svg>
    ),
  },
  WARNING: {
    label: 'Warning',
    className: styles.warning,
    icon: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5"/>
        <path d="M7 4.5v3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        <circle cx="7" cy="9.5" r="0.75" fill="currentColor"/>
      </svg>
    ),
  },
  INFO: {
    label: 'Note',
    className: styles.info,
    icon: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5"/>
        <path d="M7 6v4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        <circle cx="7" cy="4.5" r="0.75" fill="currentColor"/>
      </svg>
    ),
  },
};

export const FlagCard: React.FC<FlagCardProps> = ({ flag, index }) => {
  const [expanded, setExpanded] = useState(flag.severity === 'CRITICAL');
  const config = severityConfig[flag.severity];

  return (
    <div
      className={`${styles.card} ${config.className}`}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div className={styles.header} onClick={() => setExpanded(!expanded)}>
        <div className={styles.headerLeft}>
          <span className={`${styles.severityBadge} ${config.className}`}>
            {config.icon}
            {config.label}
          </span>
          <span className={styles.category}>{flag.category}</span>
        </div>
        <div className={styles.headerRight}>
          <span className={styles.clauseTitle}>{flag.clause_title}</span>
          <span className={`${styles.chevron} ${expanded ? styles.open : ''}`}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </span>
        </div>
      </div>

      {expanded && (
        <div className={styles.body}>
          {flag.original_text && (
            <div className={styles.excerpt}>
              <span className={styles.excerptLabel}>Contract excerpt</span>
              <blockquote className={styles.quote}>"{flag.original_text}"</blockquote>
            </div>
          )}

          <div className={styles.grid}>
            <div className={styles.gridItem}>
              <span className={styles.gridLabel}>
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M6 1L11 4V8L6 11L1 8V4L6 1Z" stroke="currentColor" strokeWidth="1.2"/>
                </svg>
                Violation
              </span>
              <p className={styles.gridValue}>{flag.violation}</p>
            </div>

            <div className={styles.gridItem}>
              <span className={styles.gridLabel}>
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <rect x="1.5" y="1.5" width="9" height="9" rx="1" stroke="currentColor" strokeWidth="1.2"/>
                  <path d="M3.5 4.5h5M3.5 6h3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
                </svg>
                Legal Reference
              </span>
              <p className={`${styles.gridValue} ${styles.legal}`}>{flag.statutory_reference}</p>
            </div>

            <div className={`${styles.gridItem} ${styles.fullWidth}`}>
              <span className={styles.gridLabel}>
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M6 1v5l3 2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
                  <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.2"/>
                </svg>
                Recommendation
              </span>
              <p className={`${styles.gridValue} ${styles.recommendation}`}>{flag.recommendation}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
