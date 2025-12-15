import type { LibrarySummary, Paginated } from '@/types';
import { Pagination, Row, Space, Typography } from 'antd';
import type React from 'react';
import { LibraryCard } from './LibraryCard';

type LibrarySectionProps = {
  title: string;
  icon?: React.ReactNode;
  libraries?: Paginated<LibrarySummary>;
  userId?: string;
  loading?: boolean;
  emptyText: string;
  onPageChange?: (page: number) => void;
  onSelect?: (id: string) => void;
};

export const LibrarySection: React.FC<LibrarySectionProps> = ({
  title,
  icon,
  libraries,
  userId,
  loading,
  emptyText,
  onPageChange,
  onSelect,
}) => {
  if (!libraries?.items.length) {
    return (
      <Typography.Paragraph type="secondary">{emptyText}</Typography.Paragraph>
    );
  }

  const pageSize = libraries.limit || 12;
  const currentPage = (libraries.offset || 0) / pageSize + 1;

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <Space align="center">
        {icon}
        <Typography.Title level={4} style={{ margin: 0 }}>
          {title}
        </Typography.Title>
      </Space>
      <Row gutter={[16, 16]}>
        {libraries.items.map((item) => (
          <LibraryCard
            key={item.library.id}
            item={item}
            loading={loading}
            isOwner={item.library.user_id === userId}
            onSelect={onSelect}
          />
        ))}
      </Row>
      <Pagination
        current={currentPage}
        total={libraries.total}
        pageSize={pageSize}
        showSizeChanger={false}
        onChange={onPageChange}
        hideOnSinglePage
      />
    </Space>
  );
};
