import {
  BookOutlined,
  ControlOutlined,
  DeploymentUnitOutlined,
  FileDoneOutlined,
  SettingOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { type MenuProps } from 'antd';
import { UserInfoCard } from './UserInfo';

export const buildMenu = (isAdmin: boolean): MenuProps['items'] => [
  {
    key: '/profile',
    style: {
      background: 'none',
      height: 'fit-content',
    },
    label: <UserInfoCard />,
  },
  {
    type: 'divider',
  },
  {
    key: '/',
    label: 'Requests',
    icon: <DeploymentUnitOutlined />,
  },
  {
    key: '/novels',
    label: 'Novels',
    icon: <BookOutlined />,
  },
  {
    key: '/meta/sources',
    label: 'Crawlers',
    icon: <FileDoneOutlined />,
  },
  {
    type: 'divider',
  },
  {
    key: '/profile',
    label: 'Profile',
    icon: <UserOutlined />,
  },
  {
    key: '/settings',
    label: 'Settings',
    icon: <SettingOutlined />,
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
        key: '/admin/users',
        label: 'Users',
        icon: <TeamOutlined />,
      },
    ],
  },
];
