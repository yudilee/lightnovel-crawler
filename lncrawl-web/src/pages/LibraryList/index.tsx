import { Auth } from '@/store/_auth';
import {
  FolderOpenOutlined,
  GlobalOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Flex, Space, Tabs, Typography } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { CreateLibraryButton } from './CreateLibraryButton';
import { LibraryList } from './LibraryList';

export const LibraryListPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const isAdmin = useSelector(Auth.select.isAdmin);

  const [refresh, setRefresh] = useState(0);

  const tab = useMemo(() => {
    return searchParams.get('tab') || 'my';
  }, [searchParams]);

  useEffect(() => {
    setSearchParams({});
  }, [isAdmin]);

  return (
    <Space size="large" direction="vertical" style={{ width: '100%' }}>
      <Flex wrap align="center" justify="space-between">
        <Typography.Title level={2} style={{ margin: 0 }}>
          <FolderOpenOutlined /> Libraries
        </Typography.Title>
        <CreateLibraryButton onSuccess={() => setRefresh((v) => v + 1)} />
      </Flex>

      {isAdmin ? (
        <LibraryList type={'all'} refreshId={refresh} />
      ) : (
        <Tabs
          activeKey={tab}
          onChange={(key) => setSearchParams({ tab: key })}
          size="large"
          tabBarGutter={24}
          items={[
            {
              key: 'my',
              label: (
                <Typography.Text style={{ color: '#39f' }}>
                  <Space>
                    <UserOutlined /> My Libraries
                  </Space>
                </Typography.Text>
              ),
              children: <LibraryList type={'my'} refreshId={refresh} />,
            },
            {
              key: 'public',
              label: (
                <Typography.Text style={{ color: '#0f0' }}>
                  <Space>
                    <GlobalOutlined /> Public Libraries
                  </Space>
                </Typography.Text>
              ),
              children: <LibraryList type={'public'} refreshId={refresh} />,
            },
          ]}
        />
      )}
    </Space>
  );
};
