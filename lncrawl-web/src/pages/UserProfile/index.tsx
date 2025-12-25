import { UserAvatar } from '@/components/Tags/UserAvatar';
import { UserRoleTag } from '@/components/Tags/UserRoleTag';
import { UserTierTag } from '@/components/Tags/UserTierTag';
import { store } from '@/store';
import { Auth } from '@/store/_auth';
import type { User } from '@/types';
import { formatDate, formatFromNow } from '@/utils/time';
import {
  CalendarOutlined,
  CrownOutlined,
  KeyOutlined,
  LockOutlined,
  MailOutlined,
  SafetyCertificateOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Descriptions, Divider, Grid, Space, Typography } from 'antd';
import axios from 'axios';
import { useSelector } from 'react-redux';
import { ProfileGenerateTokenButton } from './ProfileGenerateTokenButton';
import { ProfileNameChangeButton } from './ProfileNameChangeButton';
import { ProfilePasswordChangeButton } from './ProfilePasswordChangeButton';
import { useEffect } from 'react';

export const UserProfilePage: React.FC<any> = () => {
  const { xs } = Grid.useBreakpoint();
  const user = useSelector(Auth.select.user)!;

  const updateUser = async () => {
    const result = await axios.get<User>(`/api/auth/me`);
    store.dispatch(Auth.action.setUser(result.data));
  };

  useEffect(() => {
    updateUser();
  }, []);

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Typography.Title level={2}>
        <UserOutlined /> Profile
      </Typography.Title>

      <Descriptions
        bordered
        column={1}
        size="middle"
        layout={xs ? 'vertical' : 'horizontal'}
        styles={{ label: { width: 150, fontWeight: 500 } }}
      >
        <Descriptions.Item
          label={
            <Space>
              <UserOutlined /> Name
            </Space>
          }
        >
          <Space>
            <UserAvatar user={user} size={32} />
            <Typography.Text>{user.name}</Typography.Text>
            <Divider orientation="vertical" />
            <ProfileNameChangeButton user={user} onChange={updateUser} />
          </Space>
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <MailOutlined /> Email
            </Space>
          }
        >
          <Typography.Text copyable>{user.email}</Typography.Text>
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <SafetyCertificateOutlined /> Role
            </Space>
          }
        >
          <UserRoleTag value={user.role} />
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <CrownOutlined /> Tier
            </Space>
          }
        >
          <UserTierTag value={user.tier} />
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <CalendarOutlined /> Joined
            </Space>
          }
        >
          <Typography.Text>{formatDate(user.created_at)}</Typography.Text>
          <Divider orientation="vertical" />
          <Typography.Text type="secondary">
            {formatFromNow(user.created_at)}
          </Typography.Text>
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <LockOutlined /> Password
            </Space>
          }
        >
          <ProfilePasswordChangeButton />
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <KeyOutlined /> Token
            </Space>
          }
        >
          <ProfileGenerateTokenButton />
        </Descriptions.Item>
      </Descriptions>
    </div>
  );
};
