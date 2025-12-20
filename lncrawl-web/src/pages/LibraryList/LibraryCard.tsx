import { Auth } from '@/store/_auth';
import type { Library } from '@/types';
import { getGradientForId } from '@/utils/gradients';
import { BookOutlined, UserOutlined } from '@ant-design/icons';
import { Card, Col, Divider, Flex, Space, Tag, Typography } from 'antd';
import type React from 'react';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

export const LibraryCard: React.FC<{ library: Library }> = ({ library }) => {
  const navigate = useNavigate();
  const user = useSelector(Auth.select.user);

  const gradientBackground = useMemo(
    () => getGradientForId(library.id),
    [library.id]
  );

  return (
    <Col key={library.id} xs={24} sm={12} md={24} lg={12} xl={8}>
      <Card
        hoverable
        onClick={() => navigate(`/library/${library.id}`)}
        style={{
          height: '100%',
          border: 'none',
          overflow: 'hidden',
          position: 'relative',
          background: gradientBackground,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          textShadow: '0 2px 4px rgba(0,0,0,0.5)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
        styles={{
          body: {
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            padding: '16px 24px',
          },
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.15)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        }}
      >
        {/* Header */}
        <Flex
          justify="space-between"
          align="flex-start"
          style={{ marginBottom: 12 }}
        >
          <Space align="center" style={{ flex: 1 }}>
            <BookOutlined style={{ fontSize: 20, color: '#fff' }} />
            <Typography.Title level={5} style={{ margin: 0 }} ellipsis>
              {library.name}
            </Typography.Title>
          </Space>
          <Tag color={library.is_public ? 'green' : 'blue'}>
            {library.is_public ? 'Public' : 'Private'}
          </Tag>
        </Flex>

        {/* Description */}
        <Typography.Paragraph
          ellipsis={{ rows: 3 }}
          style={{ fontSize: 13, flex: 1 }}
        >
          {library.description || 'No description available'}
        </Typography.Paragraph>

        {/* Footer */}
        <Flex
          align="center"
          justify="space-between"
          wrap="wrap"
          style={{
            marginTop: 8,
            paddingTop: 8,
            borderTop: '1px solid rgba(255, 255, 255, 0.2)',
          }}
        >
          <Space size="small">
            <UserOutlined style={{ fontSize: 14 }} />
            <Typography.Text style={{ fontSize: 14 }}>
              {library.extra.owner_name || 'Unknown'}
              {library.user_id === user?.id ? ' (you)' : ''}
            </Typography.Text>
          </Space>
          <Divider type="vertical" />
          <Space size="small">
            <BookOutlined style={{ fontSize: 14 }} />
            <Typography.Text strong style={{ fontSize: 14 }}>
              {library.extra.novel_count || 0}{' '}
              {library.extra.novel_count === 1 ? 'Novel' : 'Novels'}
            </Typography.Text>
          </Space>
        </Flex>
      </Card>
    </Col>
  );
};
