import type { LibrarySummary } from '@/types';
import { Card, Col } from 'antd';
import type React from 'react';
import { LibraryCardBackground } from './LibraryCardBackground';
import { LibraryCardDescription } from './LibraryCardDescription';
import { LibraryCardFooter } from './LibraryCardFooter';
import { LibraryCardHeader } from './LibraryCardHeader';

type LibraryCardProps = {
  item: LibrarySummary;
  loading?: boolean;
  isOwner?: boolean;
  onSelect?: (id: string) => void;
};

export const LibraryCard: React.FC<LibraryCardProps> = ({
  item,
  loading,
  isOwner,
  onSelect,
}) => {
  return (
    <Col key={item.library.id} xs={24} sm={12} md={24} lg={12} xl={8}>
      <Card
        hoverable
        loading={loading}
        onClick={() => onSelect?.(item.library.id)}
        style={{
          height: '100%',
          overflow: 'hidden',
          position: 'relative',
          padding: 0,
          borderRadius: 12,
          border: 'none',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.15)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        }}
        styles={{
          body: {
            padding: 0,
            height: '100%',
            minHeight: 150,
          },
        }}
      >
        <LibraryCardBackground
          libraryId={item.library.id}
          novelCount={item.novel_count}
        />

        {/* Content */}
        <div
          style={{
            position: 'relative',
            zIndex: 1,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            padding: 20,
            color: 'white',
          }}
        >
          <LibraryCardHeader library={item.library} />
          <LibraryCardDescription description={item.library.description} />
          <LibraryCardFooter
            novelCount={item.novel_count}
            ownerName={item.owner.name}
            isOwner={isOwner}
          />
        </div>
      </Card>
    </Col>
  );
};
