import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { LogoutOutlined } from '@ant-design/icons';
import { Button, Flex, Typography } from 'antd';
import { useSelector } from 'react-redux';
import { UserAvatar } from '../Tags/UserAvatar';
import { EmailVerifyButton } from './EmailVerifyButton';
import { SwitchUserButton } from './SwitchUserButton';

export const UserInfoCard: React.FC<any> = () => {
  const authUser = useSelector(Auth.select.user);

  const handleLogout = () => {
    store.dispatch(Auth.action.logout());
  };

  return (
    <Flex
      gap={5}
      vertical
      align="center"
      justify="center"
      style={{
        textAlign: 'center',
        padding: '25px 0 10px 0',
      }}
    >
      <UserAvatar
        size={72}
        user={authUser}
        style={{ backgroundColor: 'blueviolet' }}
      />
      <Typography.Text strong style={{ fontSize: 16 }}>
        {authUser?.name}
      </Typography.Text>

      <div />

      <EmailVerifyButton />

      <div />

      <SwitchUserButton />

      <div />

      <Button
        block
        type="default"
        onClick={handleLogout}
        icon={<LogoutOutlined />}
        children="Logout"
      />
    </Flex>
  );
};
