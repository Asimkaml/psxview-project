import React from 'react';
import { Card } from '../components/common/Card';

export const HomePage: React.FC = () => {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card title="Watchlist" subtitle="Your saved PSX instruments.">
        <p className="text-sm text-muted">
          Watchlist management and personalized news are planned for later phases.
          For now, this area confirms the layout and visual style.
        </p>
      </Card>
      <Card title="Latest news" subtitle="Evidence-backed events affecting PSX companies.">
        <p className="text-sm text-muted">
          In this foundation phase, news is not yet wired to live data. Future
          phases will surface timestamped, sourced events here.
        </p>
      </Card>
    </div>
  );
};
