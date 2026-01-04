import LncrawlImage from '@/assets/lncrawl.svg';
import { Avatar, Divider, Grid, Layout, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { MainLayoutSidebar } from './sidebar';

export const MainLayout: React.FC<{
  noPadding?: boolean;
}> = ({ noPadding }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { md } = Grid.useBreakpoint();
  const [overlay, setOverlay] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    setCollapsed(overlay);
  }, [overlay, location.pathname]);

  return (
    <Layout>
      <Layout.Sider
        theme="light"
        breakpoint="md"
        collapsedWidth={0}
        width={250}
        collapsed={collapsed}
        onCollapse={(collapsed, type) => {
          setCollapsed(collapsed);
          if (type === 'responsive') {
            setOverlay(collapsed);
          }
        }}
        zeroWidthTriggerStyle={{
          top: '0',
        }}
        style={
          overlay
            ? {
                zIndex: 1000,
                top: 0,
                bottom: 0,
                position: 'absolute',
                boxShadow: '0 5px 10px #000',
              }
            : {
                height: '100vh',
              }
        }
      >
        <MainLayoutSidebar isCollapsed={collapsed} />
      </Layout.Sider>
      <Layout.Content
        style={{
          height: '100vh',
          overflow: 'auto',
          padding: noPadding ? 0 : md ? 20 : 10,
          paddingBottom: noPadding ? 0 : md ? 50 : 100,
        }}
        onClickCapture={() => setCollapsed(overlay)}
      >
        <div
          style={{
            margin: '0 auto',
            transition: 'all 0.2s ease-in-out',
            maxWidth: noPadding ? undefined : 1200,
            opacity: overlay && !collapsed ? '0.5' : undefined,
            pointerEvents: overlay && !collapsed ? 'none' : undefined,
            minHeight: noPadding ? 'calc(100% - 10px)' : 'calc(100% - 25px)',
          }}
        >
          {!md && (
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
          )}
          <Outlet />
        </div>
      </Layout.Content>
    </Layout>
  );
};
