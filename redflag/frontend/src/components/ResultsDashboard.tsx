import React, { useState } from 'react';
import styles from './ResultsDashboard.module.css';
import type { AnalysisResult, Severity } from '../types';
import { ScoreRing } from './ScoreRing';
import { FlagCard } from './FlagCard';
import { MetadataPanel } from './MetadataPanel';

interface ResultsDashboardProps {
  result: AnalysisResult;
}

type FilterType = 'ALL' | Severity;

const riskConfig = {
  LOW: { label: 'Low Risk', color: 'var(--success)', bg: 'var(--success-bg)', border: 'var(--success-border)' },
  MEDIUM: { label: 'Moderate Risk', color: 'var(--warning)', bg: 'var(--warning-bg)', border: 'var(--warning-border)' },
  HIGH: { label: 'High Risk', color: '#ea580c', bg: 'rgba(234,88,12,0.06)', border: 'rgba(234,88,12,0.2)' },
  CRITICAL: { label: 'Critical', color: 'var(--critical)', bg: 'var(--critical-bg)', border: 'var(--critical-border)' },
};

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ result }) => {
  const [filter, setFilter] = useState<FilterType>('ALL');

  const critical = result.flags.filter(f => f.severity === 'CRITICAL');
  const warnings = result.flags.filter(f => f.severity === 'WARNING');
  const infos = result.flags.filter(f => f.severity === 'INFO');

  const filteredFlags = filter === 'ALL' ? result.flags : result.flags.filter(f => f.severity === filter);
  const risk = riskConfig[result.overall_risk];

  return (
    <div className={styles.dashboard}>
      {/* Hero summary row */}
      <div className={styles.heroRow}>
        <div className={styles.scoreSection}>
          <ScoreRing score={result.compliance_score} risk={result.overall_risk} size={160} />
          <div className={styles.scoreLabel}>
            <span
              className={styles.riskPill}
              style={{ color: risk.color, background: risk.bg, borderColor: risk.border }}
            >
              {risk.label}
            </span>
            <p className={styles.summary}>{result.summary}</p>
          </div>
        </div>

        <div className={styles.statRow}>
          <div className={`${styles.stat} ${styles.statCritical}`}>
            <span className={styles.statNum}>{critical.length}</span>
            <span className={styles.statLabel}>Critical</span>
          </div>
          <div className={`${styles.stat} ${styles.statWarning}`}>
            <span className={styles.statNum}>{warnings.length}</span>
            <span className={styles.statLabel}>Warnings</span>
          </div>
          <div className={`${styles.stat} ${styles.statInfo}`}>
            <span className={styles.statNum}>{infos.length}</span>
            <span className={styles.statLabel}>Notes</span>
          </div>
          <div className={`${styles.stat} ${styles.statSuccess}`}>
            <span className={styles.statNum}>{result.compliant_clauses.length}</span>
            <span className={styles.statLabel}>Compliant</span>
          </div>
        </div>
      </div>

      {/* Metadata */}
      {result._meta && (
        <MetadataPanel
          metadata={result.metadata}
          filename={result._meta.filename}
          wordCount={result._meta.word_count}
        />
      )}

      {/* Flags section */}
      {result.flags.length > 0 && (
        <section className={styles.flagsSection}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>
              Compliance Flags
              <span className={styles.sectionCount}>{result.flags.length}</span>
            </h2>
            <div className={styles.filters}>
              {(['ALL', 'CRITICAL', 'WARNING', 'INFO'] as FilterType[]).map(f => (
                <button
                  key={f}
                  className={`${styles.filterBtn} ${filter === f ? styles.filterActive : ''}`}
                  onClick={() => setFilter(f)}
                >
                  {f === 'ALL' ? `All (${result.flags.length})` : f === 'CRITICAL' ? `Critical (${critical.length})` : f === 'WARNING' ? `Warning (${warnings.length})` : `Notes (${infos.length})`}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.flagsList}>
            {filteredFlags.map((flag, i) => (
              <FlagCard key={flag.id} flag={flag} index={i} />
            ))}
            {filteredFlags.length === 0 && (
              <p className={styles.emptyFilters}>No flags in this category.</p>
            )}
          </div>
        </section>
      )}

      {result.flags.length === 0 && (
        <div className={styles.allClear}>
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="var(--success)" strokeWidth="2"/>
            <path d="M10 16l4 4 8-8" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <p>No compliance issues found. This agreement appears to conform to Karnataka Rent Act requirements.</p>
        </div>
      )}

      {/* Compliant clauses */}
      {result.compliant_clauses.length > 0 && (
        <section className={styles.compliantSection}>
          <h2 className={styles.sectionTitle}>
            Compliant Clauses
            <span className={styles.sectionCount} style={{ background: 'var(--success-bg)', color: 'var(--success)', borderColor: 'var(--success-border)' }}>
              {result.compliant_clauses.length}
            </span>
          </h2>
          <div className={styles.compliantGrid}>
            {result.compliant_clauses.map((clause, i) => (
              <div key={i} className={styles.compliantCard}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="7" stroke="var(--success)" strokeWidth="1.5"/>
                  <path d="M5 8l2 2 4-4" stroke="var(--success)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <div>
                  <p className={styles.compliantCategory}>{clause.category}</p>
                  <p className={styles.compliantDesc}>{clause.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Disclaimer */}
      <div className={styles.disclaimer}>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.2"/>
          <path d="M8 7v4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
          <circle cx="8" cy="5" r="0.75" fill="currentColor"/>
        </svg>
        <p>{result.disclaimer}</p>
      </div>
    </div>
  );
};
