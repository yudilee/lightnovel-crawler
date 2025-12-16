import type { Library } from '@/types';
import { Card, Flex, Space, Switch, Tag, Typography } from 'antd';
import React from 'react';
import { DeleteLibraryButton } from './DeleteLibraryButton';
import { EditLibraryButton } from './EditLibraryButton';

interface LibraryInfoCardProps {
  library: Library;
  isOwner: boolean;
  loading: boolean;
  onTogglePublic: (checked: boolean) => void;
  onLibraryUpdated?: (updatedLibrary: Library) => void;
}

export const LibraryInfoCard: React.FC<LibraryInfoCardProps> = ({
  library,
  isOwner,
  loading,
  onTogglePublic,
  onLibraryUpdated,
}) => {
  return (
    <Card>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Flex align="center" justify="space-between" wrap>
          <Space align="center">
            <Typography.Title level={3} style={{ margin: 0 }}>
              {library.name || 'Library'}
            </Typography.Title>
            <Tag color={library.is_public ? 'green' : 'blue'}>
              {library.is_public ? 'Public' : 'Private'}
            </Tag>
          </Space>
          {isOwner && (
            <Space align="center">
              <Typography.Text>Public</Typography.Text>
              <Switch
                checked={library.is_public}
                onChange={onTogglePublic}
                disabled={loading}
              />
            </Space>
          )}
        </Flex>
        <Flex align="flex-start" justify="space-between" wrap>
          <Typography.Paragraph type="secondary" style={{ margin: 0, flex: 1 }}>
            {library.description || 'No description'}
          </Typography.Paragraph>
          {isOwner && (
            <Space>
              <EditLibraryButton
                library={library}
                onSuccess={onLibraryUpdated}
              />
              <DeleteLibraryButton library={library} />
            </Space>
          )}
        </Flex>
      </Space>
    </Card>
  );
};
