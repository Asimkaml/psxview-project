import React from 'react';
import { Card } from '../components/common/Card';

export const NewsPage: React.FC = () => {
  return (
    <Card title="News" subtitle="Evidence-backed PSX news feed.">
      <p className="text-sm text-muted">
        News cards with publisher icons, timestamps, and affected companies will
        be connected once ingestion and evidence storage are in place.
      </p>
    </Card>
  );
};
