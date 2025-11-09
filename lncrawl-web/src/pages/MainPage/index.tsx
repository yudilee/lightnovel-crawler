import { Divider, Typography } from 'antd';
import { JobListPage } from '../JobList';
import { RequestNovelCard } from '../JobList/RequestNovelCard';
import { DeploymentUnitOutlined } from '@ant-design/icons';

export const MainPage: React.FC<any> = () => {
  return (
    <>
      <RequestNovelCard />

      <Divider />

      <Typography.Title level={2}>
        <DeploymentUnitOutlined /> Your Jobs
      </Typography.Title>
      <JobListPage autoRefresh />
    </>
  );
};
