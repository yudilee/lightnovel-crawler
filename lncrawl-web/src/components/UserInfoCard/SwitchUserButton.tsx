import { UserListItemCard } from '@/pages/UserList/UserListItemCard';
import { store } from '@/store';
import { Auth } from '@/store/_auth';
import type { User } from '@/types';
import {
  CloseOutlined,
  LoginOutlined,
  UserSwitchOutlined,
} from '@ant-design/icons';
import { Button, Divider, List, Modal } from 'antd';
import { useState } from 'react';
import { useSelector } from 'react-redux';

export const SwitchUserButton: React.FC<{
  hideLoginSuggest?: boolean;
}> = ({ hideLoginSuggest }) => {
  const availableUsers = useSelector(Auth.select.availableUsers);

  const [show, setShow] = useState<boolean>(false);

  const handleLogout = () => {
    setShow(false);
    store.dispatch(Auth.action.logout());
  };

  const handleSwitch = (user: User) => {
    setShow(false);
    store.dispatch(Auth.action.switchUser(user.id));
  };

  const handleRemove = (user: User) => {
    store.dispatch(Auth.action.removeUserHistory(user.id));
  };

  if (!availableUsers.length) {
    return null;
  }

  return (
    <>
      <Button
        block
        shape="round"
        children="Switch User"
        icon={<UserSwitchOutlined />}
        onClick={() => setShow(true)}
      />

      <Modal
        centered
        open={show}
        title="Switch User"
        width={800}
        footer={null}
        onCancel={() => setShow(false)}
      >
        <List>
          {availableUsers.map((user) => (
            <div style={{ position: 'relative' }}>
              <UserListItemCard
                user={user}
                hideActions
                onClick={() => handleSwitch(user)}
              />
              <Button
                danger
                size="small"
                shape="circle"
                icon={<CloseOutlined />}
                onClick={() => handleRemove(user)}
                style={{ position: 'absolute', top: 0, right: 0 }}
              />
            </div>
          ))}
        </List>

        {!hideLoginSuggest && (
          <>
            <Divider size="small" />

            <Button
              block
              size="large"
              shape="round"
              type="primary"
              icon={<LoginOutlined />}
              onClick={handleLogout}
            >
              Login as a new user
            </Button>
          </>
        )}
      </Modal>
    </>
  );
};
