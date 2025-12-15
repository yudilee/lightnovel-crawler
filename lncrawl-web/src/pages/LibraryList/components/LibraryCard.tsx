import type { LibrarySummary } from '@/types';
import { BookOutlined, UserOutlined } from '@ant-design/icons';
import { Card, Col, Divider, Flex, Space, Tag, Typography } from 'antd';
import type React from 'react';

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
}) => (
  <Col key={item.library.id} xs={24} sm={12} md={8} lg={6} xl={6}>
    <Card
      hoverable
      loading={loading}
      onClick={() => onSelect?.(item.library.id)}
      title={
        <Space align="center">
          <BookOutlined />
          <span>{item.library.name}</span>
        </Space>
      }
      extra={
        <Tag color={item.library.is_public ? 'green' : 'blue'}>
          {item.library.is_public ? 'Public' : 'Private'}
        </Tag>
      }
      style={{ height: '100%' }}
    >
      <Typography.Paragraph type="secondary" ellipsis={{ rows: 3 }}>
        {item.library.description || 'No description'}
      </Typography.Paragraph>
      <Divider style={{ margin: '8px 0' }} />
      <Flex align="center" wrap>
        <span>{item.novel_count} Novels</span>
        <Divider type="vertical" />
        <Space size="small">
          <UserOutlined />
          <Typography.Text type="secondary">
            {item.owner.name || 'Unknown'}
            {isOwner ? ' (you)' : ''}
          </Typography.Text>
        </Space>
      </Flex>
    </Card>
  </Col>
);
