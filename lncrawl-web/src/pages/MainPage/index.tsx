import { Auth } from '@/store/_auth';
import { DeploymentUnitOutlined } from '@ant-design/icons';
import { Divider, Tabs, Typography } from 'antd';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { JobListPage } from '../JobList';
import { RequestNovelCard } from '../JobList/RequestNovelCard';

export const MainPage: React.FC<any> = () => {
  const user = useSelector(Auth.select.user);
  const isAdmin = useSelector(Auth.select.isAdmin);
  const [searchParams, setSearchParams] = useSearchParams();

  const tab = useMemo(
    () => searchParams.get('tab') || (isAdmin ? 'all' : 'my'),
    [searchParams, isAdmin]
  );

  return (
    <>
      <RequestNovelCard />

      <Divider />

      <Tabs
        activeKey={tab}
        onChange={(key) => setSearchParams({ tab: key })}
        tabBarExtraContent={{
          left: (
            <DeploymentUnitOutlined
              style={{ fontSize: 28, marginRight: 10, marginTop: 6 }}
            />
          ),
        }}
        items={[
          {
            key: 'my',
            label: (
              <Typography.Title
                level={3}
                style={{ margin: 0, color: tab === 'my' ? '' : 'gray' }}
              >
                My Requests
              </Typography.Title>
            ),
          },
          {
            key: 'all',
            label: (
              <Typography.Title
                level={3}
                style={{ margin: 0, color: tab === 'all' ? '' : 'gray' }}
              >
                All Requests
              </Typography.Title>
            ),
          },
        ]}
      />

      <JobListPage
        key={tab}
        autoRefresh
        userId={tab === 'my' ? user?.id : undefined}
      />
    </>
  );
};
