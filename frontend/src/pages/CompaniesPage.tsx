import React from 'react';
import { Card } from '../components/common/Card';

export const CompaniesPage: React.FC = () => {
  return (
    <Card title="Companies" subtitle="Research coverage for selected PSX companies.">
      <p className="text-sm text-muted">
        Company profiles and valuation views will be implemented in later phases.
        The goal in this phase is to lock in routing and layout.
      </p>
    </Card>
  );
};
