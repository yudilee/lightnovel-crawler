import { Auth } from '@/store/_auth';
import { FolderOpenOutlined } from '@ant-design/icons';
import { Flex, Space, Typography } from 'antd';
import { useSelector } from 'react-redux';
import { CreateLibraryButton } from './CreateLibraryButton';
import { LibraryList } from './LibraryList';
import { useState } from 'react';

export const LibraryListPage: React.FC = () => {
  const isAdmin = useSelector(Auth.select.isAdmin);
  const [refresh, setRefresh] = useState(0);

  const updateRefresh = () => {
    setRefresh((v) => v + 1);
  };

  return (
    <Space size="large" direction="vertical" style={{ width: '100%' }}>
      <Flex wrap align="center" justify="space-between">
        <Typography.Title level={2} style={{ margin: 0 }}>
          <FolderOpenOutlined /> Libraries
        </Typography.Title>
        <CreateLibraryButton onSuccess={updateRefresh} />
      </Flex>

      {isAdmin ? (
        <LibraryList
          type={'all'}
          refreshId={refresh}
          updateRefresh={updateRefresh}
        />
      ) : (
        <>
          <LibraryList
            type={'my'}
            refreshId={refresh}
            updateRefresh={updateRefresh}
          />
          <LibraryList
            type={'public'}
            refreshId={refresh}
            updateRefresh={updateRefresh}
          />
        </>
      )}
    </Space>
  );
};
