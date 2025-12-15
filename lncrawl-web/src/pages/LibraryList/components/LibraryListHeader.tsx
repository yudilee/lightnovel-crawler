import { FolderAddOutlined } from '@ant-design/icons';
import { Button, Flex, Space, Typography } from 'antd';
import type React from 'react';

type LibraryListHeaderProps = {
  onCreateClick: () => void;
};

export const LibraryListHeader: React.FC<LibraryListHeaderProps> = ({
  onCreateClick,
}) => (
  <Flex justify="space-between" align="center" wrap>
    <Typography.Title level={2} style={{ margin: 0 }}>
      Libraries
    </Typography.Title>
    <Space>
      <Button
        icon={<FolderAddOutlined />}
        type="primary"
        onClick={onCreateClick}
      >
        New Library
      </Button>
    </Space>
  </Flex>
);
