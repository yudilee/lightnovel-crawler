import { UserRoleTag } from '@/components/Tags/UserRoleTag';
import { UserTierTag } from '@/components/Tags/UserTierTag';
import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { UserRole, UserTier, type User } from '@/types';
import { stringifyError } from '@/utils/errors';
import { EditOutlined, SaveOutlined } from '@ant-design/icons';
import {
  Button,
  Divider,
  Flex,
  Form,
  Input,
  Modal,
  Select,
  Space,
  message,
  type ButtonProps,
} from 'antd';
import axios from 'axios';
import { useState } from 'react';

export const UserEditButton: React.FC<
  {
    user: User;
    onChange?: () => any;
  } & ButtonProps
> = ({ user, onChange, ...buttonProps }) => {
  const [messageApi, contextHolder] = message.useMessage();

  const [editOpen, setEditOpen] = useState(false);
  const [updating, setUpdating] = useState(false);

  const handleUpdateName = async (values: {
    name?: string;
    password?: string;
    role?: string;
    tier?: number;
  }) => {
    try {
      setUpdating(true);
      const changes: any = {};
      if (values.password?.trim()) {
        changes.password = values.password.trim();
      }
      if (typeof values.role === 'string' && values.role !== user.role) {
        changes.role = values.role;
      }
      if (typeof values.tier === 'number' && values.tier !== user.tier) {
        changes.tier = values.tier;
      }
      if (values.name?.trim() && values.name?.trim() !== user.name) {
        changes.name = values.name;
      }
      if (!Object.keys(changes).length) {
        messageApi.info('No value was updated');
        return;
      }
      await axios.put(`/api/user/${user.id}`, changes);
      delete changes.password;
      store.dispatch(Auth.action.setUser({ ...user, ...changes }));
      messageApi.success('User updated successfully');
      setEditOpen(false);
      if (onChange) onChange();
    } catch (err) {
      console.error(err);
      messageApi.error(stringifyError(err));
    } finally {
      setUpdating(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Button
        icon={<EditOutlined />}
        {...buttonProps}
        onClick={() => setEditOpen(true)}
      >
        Edit User
      </Button>

      <Modal
        title={
          <Space>
            <EditOutlined /> Edit Name
          </Space>
        }
        open={editOpen}
        footer={null}
        onCancel={() => setEditOpen(false)}
        destroyOnHidden
      >
        <Form
          layout="vertical"
          initialValues={user}
          onFinish={handleUpdateName}
          labelCol={{ style: { padding: 0 } }}
        >
          <Form.Item
            name="name"
            label="Full Name"
            rules={[
              {
                validator: (_, value) =>
                  value && value.trim().length >= 2
                    ? Promise.resolve()
                    : Promise.reject('Please enter a valid name'),
              },
            ]}
          >
            <Input
              size="large"
              placeholder="Enter full name"
              autoComplete="name"
            />
          </Form.Item>

          <Form.Item name="role" label="Role">
            <Select
              size="large"
              placeholder="Select role"
              options={Object.values(UserRole).map((value) => ({
                value,
                label: <UserRoleTag value={value} />,
              }))}
            />
          </Form.Item>

          <Form.Item name="tier" label="Tier">
            <Select
              size="large"
              placeholder="Select tier"
              options={Object.values(UserTier).map((value) => ({
                value,
                label: <UserTierTag value={value} />,
              }))}
            />
          </Form.Item>

          <Form.Item
            name={'password'}
            label="Password"
            rules={[
              { min: 6, message: 'Password must be at least 6 characters' },
            ]}
            hasFeedback
          >
            <Input.Password
              size="large"
              placeholder="New password"
              autoComplete="new-password"
            />
          </Form.Item>

          <Divider size="small" />

          <Flex gap={10} justify="end">
            <Button onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button
              type="primary"
              htmlType="submit"
              loading={updating}
              icon={<SaveOutlined />}
            >
              Save
            </Button>
          </Flex>
        </Form>
      </Modal>
    </>
  );
};
