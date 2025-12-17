import type { Library } from '@/types';
import { getGradientForId } from '@/utils/gradients';
import { BookOutlined } from '@ant-design/icons';
import { Card, Flex, Space, Switch, Tag, Typography } from 'antd';
import { useMemo } from 'react';
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
  const gradientBackground = useMemo(
    () => getGradientForId(library.id),
    [library.id]
  );

  return (
    <Card
      style={{
        position: 'relative',
        overflow: 'hidden',
        background: gradientBackground,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        textShadow: '0 2px 4px rgba(0,0,0,0.5)',
      }}
      styles={{
        body: {
          display: 'flex',
          position: 'relative',
          justifyContent: 'space-between',
        },
      }}
    >
      {/* Cover Image */}
      <BookOutlined style={{ fontSize: 48, color: '#fff', marginRight: 16 }} />

      {/* Content */}
      <Flex vertical justify="center" style={{ width: '100%' }}>
        <Space>
          <Typography.Title level={3} style={{ margin: 0 }}>
            {library.name || 'Library'}
          </Typography.Title>
          <Tag color={library.is_public ? 'green' : 'blue'}>
            {library.is_public ? 'Public' : 'Private'}
          </Tag>
        </Space>
        <Typography.Paragraph type="secondary" style={{ margin: 0, flex: 1 }}>
          {library.description || 'No description'}
        </Typography.Paragraph>
      </Flex>

      {/* Owner Controls */}
      {isOwner && (
        <Flex vertical align="flex-end" gap={7} style={{ width: 250 }}>
          <Flex align="center" gap={8} wrap justify="end">
            <Typography.Text>Public</Typography.Text>
            <Switch
              checked={library.is_public}
              onChange={onTogglePublic}
              disabled={loading}
            />
          </Flex>

          <Flex gap={4} align="center" wrap justify="end">
            <EditLibraryButton library={library} onSuccess={onLibraryUpdated} />
            <DeleteLibraryButton library={library} />
          </Flex>
        </Flex>
      )}
    </Card>
  );
};
