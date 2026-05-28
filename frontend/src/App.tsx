import { useState } from 'react';
import './index.css';
import { Header } from './components/Header';
import { HeroSection } from './components/HeroSection';
import { UploadZone } from './components/UploadZone';
import { ResultsDashboard } from './components/ResultsDashboard';
import { analyzeContract } from './api/client';
import type { AnalysisState } from './types';
import styles from './App.module.css';

function App() {
  const [state, setState] = useState<AnalysisState>({ status: 'idle' });

  const handleFile = async (file: File) => {
    setState({ status: 'uploading' });
    try {
      setState({ status: 'analyzing' });
      const result = await analyzeContract(file);
      setState({ status: 'done', result });
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        'An unexpected error occurred. Please try again.';
      setState({ status: 'error', message });
    }
  };

  const handleReset = () => {
    setState({ status: 'idle' });
  };

  const isDone = state.status === 'done';

  return (
    <div className={styles.app}>
      <Header onReset={handleReset} showReset={isDone} />

      <main className={styles.main}>
        <div className={`${styles.layout} ${isDone ? styles.resultLayout : ''}`}>

          {!isDone && (
            <div className={styles.leftPane}>
              <HeroSection />
            </div>
          )}

          <div className={styles.rightPane}>
            {state.status === 'idle' && (
              <div className={styles.uploadCard}>
                <div className={styles.uploadCardHeader}>
                  <h2 className={styles.uploadTitle}>Analyse Your Contract</h2>
                  <p className={styles.uploadSubtitle}>Upload a rental agreement PDF to get started</p>
                </div>
                <UploadZone onFile={handleFile} isLoading={false} />
              </div>
            )}

            {(state.status === 'uploading' || state.status === 'analyzing') && (
              <div className={styles.uploadCard}>
                <div className={styles.uploadCardHeader}>
                  <h2 className={styles.uploadTitle}>Analyse Your Contract</h2>
                  <p className={styles.uploadSubtitle}>Running statutory compliance checks…</p>
                </div>
                <UploadZone onFile={handleFile} isLoading={true} />
              </div>
            )}

            {state.status === 'error' && (
              <div className={styles.errorCard}>
                <div className={styles.errorIcon}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5"/>
                    <path d="M12 7v6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <circle cx="12" cy="17" r="1" fill="currentColor"/>
                  </svg>
                </div>
                <div>
                  <p className={styles.errorTitle}>Analysis Failed</p>
                  <p className={styles.errorMessage}>{state.message}</p>
                </div>
                <button className={styles.retryBtn} onClick={handleReset}>Try Again</button>
              </div>
            )}
          </div>

          {isDone && state.status === 'done' && (
            <div className={styles.resultsPane}>
              <ResultsDashboard result={state.result} />
            </div>
          )}
        </div>
      </main>

      <footer className={styles.footer}>
        <p>
          RedFlag is an automated compliance search engine, not a law firm.
          {' '}<a href="https://karnataka.gov.in" target="_blank" rel="noopener noreferrer">
            Karnataka Rent (Amendment) Act 2025/26
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
