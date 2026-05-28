import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import styles from './UploadZone.module.css';

interface UploadZoneProps {
  onFile: (file: File) => void;
  isLoading: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onFile, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFile(acceptedFiles[0]);
    }
    setDragActive(false);
  }, [onFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: isLoading,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  return (
    <div className={styles.wrapper}>
      <div
        {...getRootProps()}
        className={`${styles.dropzone} ${isDragActive || dragActive ? styles.active : ''} ${isLoading ? styles.loading : ''}`}
      >
        <input {...getInputProps()} />

        <div className={styles.content}>
          {isLoading ? (
            <div className={styles.loadingState}>
              <div className={styles.spinner} />
              <p className={styles.loadingText}>Analyzing your contract…</p>
              <p className={styles.loadingSubtext}>Running compliance checks against Karnataka Rent Act 2025/26</p>
            </div>
          ) : (
            <>
              <div className={styles.iconWrap}>
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none" className={styles.icon}>
                  <path d="M8 32h24M20 8v18M13 15l7-7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className={styles.textGroup}>
                <p className={styles.primary}>
                  {isDragActive ? 'Drop your agreement here' : 'Upload Rental Agreement'}
                </p>
                <p className={styles.secondary}>
                  Drag & drop your PDF or <span className={styles.link}>browse files</span>
                </p>
                <p className={styles.hint}>Supports PDF · Max 10MB · Processed locally, deleted immediately</p>
              </div>
            </>
          )}
        </div>

        <div className={styles.cornerTL} />
        <div className={styles.cornerTR} />
        <div className={styles.cornerBL} />
        <div className={styles.cornerBR} />
      </div>

      <div className={styles.privacyNote}>
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M7 1L2 3v4c0 3 2.2 5.5 5 6 2.8-.5 5-3 5-6V3L7 1z" stroke="currentColor" strokeWidth="1.2" fill="none"/>
          <path d="M4.5 7l2 2 3-3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        <span>Your document is never stored. Zero-retention processing — parsed in RAM and deleted immediately after analysis.</span>
      </div>
    </div>
  );
};
