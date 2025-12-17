import {
  BookOutlined,
  ControlOutlined,
  DeploymentUnitOutlined,
  FileDoneOutlined,
  FolderAddOutlined,
  FolderOpenOutlined,
  SettingOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { type MenuProps } from 'antd';
import { Link } from 'react-router-dom';
import { UserInfoCard } from '../UserInfoCard';

interface BuildMenuProps {
  isAdmin: boolean;
  currentPath: string;
}

function getClassName(currentPath: string, path: string): string | undefined {
  if (currentPath === path) {
    return 'ant-menu-item-selected';
  }
  return undefined;
}

export const buildMenu = ({
  isAdmin,
  currentPath,
}: BuildMenuProps): MenuProps['items'] => [
  {
    type: 'group',
    label: <UserInfoCard />,
    style: {
      background: 'none',
      height: 'fit-content',
    },
  },
  {
    type: 'divider',
  },
  {
    key: 'requests',
    icon: <DeploymentUnitOutlined />,
    label: <Link to="/">Requests</Link>,
    className: getClassName(currentPath, '/'),
  },
  {
    key: 'novels',
    icon: <BookOutlined />,
    label: <Link to="/novels">Novels</Link>,
    className: getClassName(currentPath, '/novels'),
  },
  {
    key: 'libraries',
    icon: <FolderOpenOutlined />,
    label: <Link to="/libraries">Libraries</Link>,
  },
  {
    key: 'my-libraries',
    icon: <FolderAddOutlined />,
    label: <Link to="/libraries/my">My Libraries</Link>,
    className: getClassName(currentPath, '/libraries/my'),
    style: {
      paddingLeft: 32,
      display: currentPath.startsWith('/libraries') ? undefined : 'none',
    },
  },
  {
    key: 'crawlers',
    icon: <FileDoneOutlined />,
    label: <Link to="/meta/sources">Crawlers</Link>,
    className: getClassName(currentPath, '/meta/sources'),
  },
  {
    type: 'divider',
  },
  {
    key: 'profile',
    icon: <UserOutlined />,
    label: <Link to="/profile">Profile</Link>,
    className: getClassName(currentPath, '/profile'),
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: <Link to="/settings">Settings</Link>,
    className: getClassName(currentPath, '/settings'),
  },
  {
    type: 'divider',
    style: { display: isAdmin ? undefined : 'none' },
  },
  {
    key: 'admin',
    label: 'Administration',
    icon: <ControlOutlined />,
    style: { display: isAdmin ? undefined : 'none' },
    children: [
      {
        key: 'admin-users',
        icon: <TeamOutlined />,
        label: <Link to="/admin/users">Users</Link>,
        className: getClassName(currentPath, '/admin/users'),
      },
    ],
  },
];
