import { Divider, Typography } from 'antd';
import { JobListPage } from '../JobList';
import { RequestNovelCard } from '../JobList/RequestNovelCard';
import { DeploymentUnitOutlined } from '@ant-design/icons';

export const MainPage: React.FC<any> = () => {
  return (
    <>
      <RequestNovelCard />

      <Divider />

      <JobListPage
        autoRefresh
        title={
          <Typography.Title level={2}>
            <DeploymentUnitOutlined /> My Requests
          </Typography.Title>
        }
      />
    </>
  );
};
