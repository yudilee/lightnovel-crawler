import { Auth } from '@/store/_auth';
import {
  BookOutlined,
  CommentOutlined,
  ControlOutlined,
  DeploymentUnitOutlined,
  FileDoneOutlined,
  FolderOpenOutlined,
  HeartOutlined,
  QuestionCircleOutlined,
  SettingOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Button, Flex, Menu } from 'antd';
import { useSelector } from 'react-redux';
import { Link, useLocation } from 'react-router-dom';
import { UserInfoCard } from '../UserInfoCard';

function getClassName(currentPath: string, path: string): string | undefined {
  if (currentPath === path) {
    return 'ant-menu-item-selected';
  }
  return undefined;
}

export const MainLayoutSidebar: React.FC<any> = () => {
  const { pathname: currentPath } = useLocation();
  const isAdmin = useSelector(Auth.select.isAdmin);

  return (
    <Flex vertical style={{ height: '100%' }}>
      <Menu
        key={currentPath}
        mode="inline"
        inlineIndent={15}
        defaultOpenKeys={[
          'admin', // keep open by default
        ]}
        style={{ flex: 1, overflow: 'auto' }}
      >
        <Menu.ItemGroup
          title={<UserInfoCard />}
          style={{
            background: 'none',
            height: 'fit-content',
          }}
        />
        <Menu.Divider />
        <Menu.Item
          icon={<DeploymentUnitOutlined />}
          className={getClassName(currentPath, '/')}
        >
          <Link to="/">Requests</Link>
        </Menu.Item>
        <Menu.Item
          icon={<BookOutlined />}
          className={getClassName(currentPath, '/novels')}
        >
          <Link to="/novels">Novels</Link>
        </Menu.Item>
        <Menu.Item
          icon={<FolderOpenOutlined />}
          className={getClassName(currentPath, '/libraries')}
        >
          <Link to="/libraries">Libraries</Link>
        </Menu.Item>
        <Menu.Item
          icon={<FileDoneOutlined />}
          className={getClassName(currentPath, '/meta/sources')}
        >
          <Link to="/meta/sources">Crawlers</Link>
        </Menu.Item>
        <Menu.Item
          icon={<CommentOutlined />}
          className={getClassName(currentPath, '/feedbacks')}
        >
          <Link to="/feedbacks">Feedbacks</Link>
        </Menu.Item>
        <Menu.Divider />
        <Menu.Item
          icon={<UserOutlined />}
          className={getClassName(currentPath, '/profile')}
        >
          <Link to="/profile">Profile</Link>
        </Menu.Item>
        <Menu.Item
          icon={<SettingOutlined />}
          className={getClassName(currentPath, '/settings')}
        >
          <Link to="/settings">Settings</Link>
        </Menu.Item>
        <Menu.Divider />
        <Menu.Item
          icon={<QuestionCircleOutlined />}
          className={getClassName(currentPath, '/tutorial')}
        >
          <Link to="/tutorial">Tutorial</Link>
        </Menu.Item>
        {isAdmin && <Menu.Divider />}
        {isAdmin && (
          <Menu.SubMenu
            key="admin"
            title="Administration"
            icon={<ControlOutlined />}
          >
            <Menu.Item
              icon={<TeamOutlined />}
              className={getClassName(currentPath, '/admin/users')}
            >
              <Link to="/admin/users">Users</Link>
            </Menu.Item>
          </Menu.SubMenu>
        )}
      </Menu>
      <div style={{ padding: '12px 16px' }}>
        <Button
          type="primary"
          icon={<HeartOutlined twoToneColor="red" />}
          block
          href="https://paypal.me/bitan0n"
          target="_blank"
          rel="noopener noreferrer"
        >
          Donate
        </Button>
      </div>
    </Flex>
  );
};
