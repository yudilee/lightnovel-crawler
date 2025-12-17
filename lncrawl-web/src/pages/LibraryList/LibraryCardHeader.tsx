import type { Library } from '@/types';
import { BookOutlined } from '@ant-design/icons';
import { Flex, Space, Tag, Typography } from 'antd';
import type React from 'react';

export const LibraryCardHeader: React.FC<{
  library: Library;
}> = ({ library }) => {
  return (
    <Flex
      justify="space-between"
      align="flex-start"
      style={{ marginBottom: 12 }}
    >
      <Space align="center" style={{ flex: 1 }}>
        <BookOutlined style={{ fontSize: 20, color: '#fff' }} />
        <Typography.Title
          level={5}
          style={{
            margin: 0,
            color: '#fff',
            fontWeight: 600,
            textShadow: '0 2px 4px rgba(0,0,0,0.5)',
          }}
          ellipsis
        >
          {library.name}
        </Typography.Title>
      </Space>
      <Tag
        color={library.is_public ? 'green' : 'blue'}
        style={{
          margin: 0,
          border: 'none',
          fontWeight: 500,
        }}
      >
        {library.is_public ? 'Public' : 'Private'}
      </Tag>
    </Flex>
  );
};
