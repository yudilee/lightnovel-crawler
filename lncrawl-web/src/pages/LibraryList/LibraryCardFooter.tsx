import { BookOutlined, UserOutlined } from '@ant-design/icons';
import { Divider, Flex, Space, Typography } from 'antd';
import type React from 'react';

type LibraryCardFooterProps = {
  novelCount: number;
  ownerName?: string;
  isOwner?: boolean;
};

export const LibraryCardFooter: React.FC<LibraryCardFooterProps> = ({
  novelCount,
  ownerName,
  isOwner,
}) => {
  return (
    <Flex
      align="center"
      justify="space-between"
      wrap="wrap"
      style={{
        marginTop: 16,
        paddingTop: 16,
        borderTop: '1px solid rgba(255, 255, 255, 0.2)',
      }}
    >
      <Space size="small">
        <UserOutlined style={{ fontSize: 14 }} />
        <Typography.Text
          style={{
            color: 'rgba(255, 255, 255, 0.9)',
            textShadow: '0 1px 2px rgba(0,0,0,0.5)',
            fontSize: 13,
          }}
        >
          {ownerName || 'Unknown'}
          {isOwner ? ' (you)' : ''}
        </Typography.Text>
      </Space>
      <Divider type="vertical" />
      <Space size="small">
        <BookOutlined style={{ fontSize: 14 }} />
        <Typography.Text
          strong
          style={{
            color: '#fff',
            textShadow: '0 1px 2px rgba(0,0,0,0.5)',
            fontSize: 14,
          }}
        >
          {novelCount} {novelCount === 1 ? 'Novel' : 'Novels'}
        </Typography.Text>
      </Space>
    </Flex>
  );
};
