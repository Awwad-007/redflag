import React, { useEffect, useRef } from 'react';
import styles from './ScoreRing.module.css';
import type { RiskLevel } from '../types';

interface ScoreRingProps {
  score: number;
  risk: RiskLevel;
  size?: number;
}

const riskColors: Record<RiskLevel, string> = {
  LOW: '#1a7a45',
  MEDIUM: '#c47d0e',
  HIGH: '#ea580c',
  CRITICAL: '#c0392b',
};

const riskLabels: Record<RiskLevel, string> = {
  LOW: 'Low Risk',
  MEDIUM: 'Moderate Risk',
  HIGH: 'High Risk',
  CRITICAL: 'Critical',
};

export const ScoreRing: React.FC<ScoreRingProps> = ({ score, risk, size = 160 }) => {
  const circleRef = useRef<SVGCircleElement>(null);
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const targetOffset = circumference - (score / 100) * circumference;
  const color = riskColors[risk];

  useEffect(() => {
    const el = circleRef.current;
    if (!el) return;
    el.style.setProperty('--dash-offset', String(targetOffset));
    el.style.strokeDashoffset = String(circumference);
    const timer = setTimeout(() => {
      el.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
      el.style.strokeDashoffset = String(targetOffset);
    }, 200);
    return () => clearTimeout(timer);
  }, [score, targetOffset, circumference]);

  return (
    <div className={styles.container}>
      <svg width={size} height={size} viewBox="0 0 100 100">
        {/* Track */}
        <circle
          cx="50" cy="50" r={radius}
          fill="none"
          stroke="var(--surface-3)"
          strokeWidth="8"
        />
        {/* Progress */}
        <circle
          ref={circleRef}
          cx="50" cy="50" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          transform="rotate(-90 50 50)"
          style={{ filter: `drop-shadow(0 0 6px ${color}40)` }}
        />
      </svg>
      <div className={styles.labelGroup}>
        <span className={styles.score} style={{ color }}>{score}</span>
        <span className={styles.label}>/ 100</span>
        <span className={styles.riskLabel} style={{ color }}>{riskLabels[risk]}</span>
      </div>
    </div>
  );
};
