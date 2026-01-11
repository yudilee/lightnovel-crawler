import LncrawlImage from '@/assets/lncrawl.svg';
import { Avatar, Divider, Grid, Layout, Typography } from 'antd';
import { Outlet, useNavigate } from 'react-router-dom';
import { MainLayoutSidebar } from './sidebar';
import { MobileNavbar } from './navbar';

export const MainLayout: React.FC<{
  noPadding?: boolean;
}> = ({ noPadding }) => {
  const { md } = Grid.useBreakpoint();

  return (
    <Layout>
      {md && <MainLayoutSidebar />}
      <Layout.Content
        style={{
          height: '100vh',
          overflow: 'auto',
          position: 'relative',
          padding: noPadding ? 0 : md ? 20 : 10,
          paddingBottom: noPadding ? 0 : md ? 50 : 100,
        }}
      >
        {!md && <MobileTopBar noPadding={noPadding} />}
        <Outlet />
      </Layout.Content>
      {!md && <MobileNavbar />}
    </Layout>
  );
};

const MobileTopBar: React.FC<{
  noPadding?: boolean;
}> = ({ noPadding }) => {
  const navigate = useNavigate();
  return (
    <>
      <Typography.Title
        onClick={() => navigate('/')}
        level={4}
        style={{
          textAlign: 'center',
          fontSize: 18,
          margin: noPadding ? 7 : 0,
        }}
      >
        <Avatar
          shape="square"
          src={LncrawlImage}
          size={24}
          style={{ paddingBottom: 3 }}
        />
        Lightnovel Crawler
      </Typography.Title>
      {!noPadding && <Divider size="small" />}
    </>
  );
};
