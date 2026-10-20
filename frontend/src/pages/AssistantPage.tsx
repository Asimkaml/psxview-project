import React from 'react';
import { Card } from '../components/common/Card';

export const AssistantPage: React.FC = () => {
  return (
    <Card title="Research assistant" subtitle="Evidence-backed Q&A for PSX investors.">
      <p className="text-sm text-muted">
        The conversational assistant will be wired to stored evidence and a
        replaceable AI provider in a later phase. For now this route reserves
        the experience and verifies navigation.
      </p>
    </Card>
  );
};
