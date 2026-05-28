import React from 'react';
import styles from './MetadataPanel.module.css';
import type { ContractMetadata } from '../types';

interface MetadataPanelProps {
  metadata: ContractMetadata;
  filename: string;
  wordCount: number;
}

export const MetadataPanel: React.FC<MetadataPanelProps> = ({ metadata, filename, wordCount }) => {
  const fields: { label: string; value: string | null; icon: string }[] = [
    { label: 'Agreement Type', value: metadata.agreement_type, icon: '📄' },
    { label: 'Tenant', value: metadata.tenant_name, icon: '👤' },
    { label: 'Landlord', value: metadata.landlord_name, icon: '🏠' },
    { label: 'Property', value: metadata.property_address, icon: '📍' },
    { label: 'Monthly Rent', value: metadata.monthly_rent, icon: '₹' },
    { label: 'Security Deposit', value: metadata.security_deposit, icon: '🔒' },
    { label: 'Duration', value: metadata.lease_duration, icon: '📅' },
    { label: 'Start Date', value: metadata.commencement_date, icon: '🗓️' },
  ];

  const presentFields = fields.filter(f => f.value && f.value !== 'UNKNOWN');

  return (
    <div className={styles.panel}>
      <div className={styles.panelHeader}>
        <h3 className={styles.title}>Contract Details</h3>
        <span className={styles.filenameTag}>{filename}</span>
      </div>

      <div className={styles.fieldGrid}>
        {presentFields.map(field => (
          <div key={field.label} className={styles.field}>
            <span className={styles.fieldLabel}>{field.label}</span>
            <span className={styles.fieldValue}>{field.value}</span>
          </div>
        ))}
        <div className={styles.field}>
          <span className={styles.fieldLabel}>Document Size</span>
          <span className={styles.fieldValue}>{wordCount.toLocaleString()} words</span>
        </div>
      </div>
    </div>
  );
};
